import pytest

from app.scrapers import BaseScraper, TemporadaLivreScraper


@pytest.mark.parametrize(
    "text, expected",
    [
        ("R$ 450", 450.0),
        ("R$ 1.200", 1200.0),
        ("R$ 1.200,50", 1200.5),
        ("R$ 450,00", 450.0),
        ("790", 790.0),
        ("", 0.0),
        ("Consulte", 0.0),
    ],
)
def test_extract_price(text, expected):
    assert BaseScraper._extract_price(text) == expected


def test_mentions_pets_uses_whole_words():
    assert BaseScraper._mentions_pets("aceita pets e crianças")
    assert BaseScraper._mentions_pets("aceitamos animais")
    assert not BaseScraper._mentions_pets("casa em petrópolis com carpete")


@pytest.mark.parametrize(
    "title, expected",
    [
        ("Sítio Bela Vista com lago", "sitio"),
        ("Chácara com piscina", "chacara"),
        ("Apartamento pé na areia", "casa"),
        ("Casa de campo", "casa"),
        ("Chácara / sítio", "chacara"),
    ],
)
def test_classify_property_type(title, expected):
    assert BaseScraper._classify_property_type(title) == expected


TL_PAGE = """
<a class="show-details" href="/aluguel-temporada/brasil/sao-paulo/atibaia/portao/12345-chacara-top">
  <div class="image"><img src="https://s.temporadalivre.com/a.jpg"></div>
  <span class="title">Chácara Top</span>
  <div class="numbers">12 Pessoas 4 Quartos</div>
  <div class="location">Chácara em Atibaia / Portão</div>
  <span class="price">R$ <span data-behavior="rate">1.500</span></span>
</a>
<a class="show-details" href="/aluguel-temporada/brasil/santa-catarina/bombinhas/centro/67890-apto">
  <span class="title">Apto destaque</span>
  <span class="price">R$ <span data-behavior="rate">300</span></span>
</a>
"""


@pytest.mark.asyncio
async def test_temporadalivre_ignores_listings_from_other_cities():
    scraper = TemporadaLivreScraper()

    async def fake_fetch(url, params=None):
        return TL_PAGE

    scraper.fetch_html = fake_fetch
    results = await scraper.search("Atibaia", "SP")

    assert [r.external_id for r in results] == ["12345"]
    prop = results[0]
    assert prop.url.startswith("https://www.temporadalivre.com/aluguel-temporada/brasil/sao-paulo/atibaia/")
    assert prop.daily_rate == 1500.0
    assert prop.property_type == "chacara"
    assert prop.max_guests == 12
    assert prop.neighborhood == "Portão"
