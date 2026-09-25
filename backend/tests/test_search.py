import pytest

from app.schemas.search import SearchQuery
from app.scrapers import ScrapedProperty
from app.services.search_service import search_service


@pytest.mark.asyncio
async def test_search_service_aggregation():
    query = SearchQuery(
        city="Atibaia",
        state="SP",
        guests=10,
        property_type="chacara",
    )
    response = await search_service.search(query)

    assert response.city == "Atibaia"
    assert response.total_results >= 1
    assert len(response.results) >= 1

    first = response.results[0]
    assert first.max_guests >= 10
    assert first.lowest_daily_rate > 0
    assert len(first.platforms) >= 1
    assert first.best_platform in ["TemporadaLivre", "OLX Imóveis"]


def _prop(platform, ext_id, title, daily_rate, bedrooms=3):
    return ScrapedProperty(
        platform=platform,
        external_id=ext_id,
        title=title,
        url=f"https://{platform}.example/{ext_id}",
        city="Ubatuba",
        state="SP",
        daily_rate=daily_rate,
        bedrooms=bedrooms,
        images=[f"https://{platform}.example/{ext_id}.jpg"],
    )


def test_group_never_merges_listings_from_same_platform():
    items = search_service._group_properties(
        [
            _prop("olx", "1", "Casa em Ubatuba com piscina", 400),
            _prop("olx", "2", "Casa em Ubatuba com piscina!", 300),
        ],
        nights=2,
    )
    assert len(items) == 2
    for item in items:
        assert len(item.platforms) == 1
        assert item.images == [f"https://olx.example/{item.platforms[0].external_id}.jpg"]


def test_group_matches_same_property_across_platforms():
    items = search_service._group_properties(
        [
            _prop("temporadalivre", "10", "CASA PRAIA DE MARANDUBA SIMONE", 500),
            _prop("olx", "20", "Casa Praia de Maranduba - Simone", 450),
            _prop("olx", "30", "Apartamento Praia Grande Ubatuba", 450),
        ],
        nights=2,
    )
    assert len(items) == 2
    grouped = next(i for i in items if len(i.platforms) == 2)
    assert [p.external_id for p in grouped.platforms if p.is_cheapest] == ["20"]


def test_cache_key_varies_with_filters():
    base = SearchQuery(city="Atibaia", state="SP")
    keys = {
        search_service._generate_cache_key(q)
        for q in [
            base,
            base.model_copy(update={"has_pool": True}),
            base.model_copy(update={"sort_by": "price_desc"}),
            base.model_copy(update={"page": 2}),
        ]
    }
    assert len(keys) == 4
