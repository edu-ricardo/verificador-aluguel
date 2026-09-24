import pytest

from app.schemas.search import SearchQuery
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
