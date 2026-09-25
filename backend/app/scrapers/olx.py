import re
from datetime import date
from typing import List, Optional

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ScrapedProperty, logger


class OLXScraper(BaseScraper):
    platform_name = "OLX Imóveis"
    platform_code = "olx"
    base_url = "https://www.olx.com.br"

    async def search(
        self,
        city: str,
        state: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        guests: int = 1,
        property_type: Optional[str] = None,
    ) -> List[ScrapedProperty]:
        state_code = (state or "sp").lower()
        # Categoria "Imóveis > Temporada". ("aluguel-de-temporada" não é uma categoria da OLX: a página
        # lista todos os imóveis, inclusive vendas, e só o termo "temporada" na busca filtrava algo.)
        url = f"{self.base_url}/imoveis/temporada/estado-{state_code}"
        html = await self.fetch_html(url, params={"q": city})

        results: List[ScrapedProperty] = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("section.olx-adcard, section[class*='olx-adcard'], div[data-testid='adcard']")
            seen_ids = set()

            for card in cards:
                try:
                    link_elem = card.select_one("a.olx-adcard__link, a[data-testid='adcard-link'], a[href*='temporada']")
                    if not link_elem:
                        continue

                    href = link_elem.get("href", "")
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"{self.base_url}{href}"

                    # Prioriza anúncios de aluguel por temporada e ignora vendas
                    ext_match = re.search(r"-(\d+)$", href.split("?")[0])
                    ext_id = ext_match.group(1) if ext_match else href
                    if ext_id in seen_ids:
                        continue
                    seen_ids.add(ext_id)

                    title_elem = card.select_one("h2.olx-adcard__title, .olx-adcard__title, h2")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    price_elem = card.select_one("h3.olx-adcard__price, .olx-adcard__price")
                    daily_rate = self._extract_price(price_elem.get_text(strip=True)) if price_elem else 0.0

                    # Sem preço não há o que comparar; preço astronômico indica anúncio de venda
                    if daily_rate <= 0 or daily_rate > 25000:
                        continue

                    img_elem = card.select_one("img")
                    img_url = ""
                    if img_elem:
                        img_url = img_elem.get("src") or img_elem.get("data-src") or ""
                        if not img_url.startswith("http"):
                            img_url = ""  # placeholder lazy-load (data:image/...) não é foto do anúncio

                    card_text = card.get_text(" ").lower()
                    has_pool = "piscina" in card_text
                    allows_pets = self._mentions_pets(card_text)
                    has_bbq = "churrasqueira" in card_text or "churras" in card_text or "gourmet" in card_text

                    # Quartos
                    bedrooms = 3
                    detail_texts = [d.get_text(strip=True) for d in card.select(".olx-adcard__detail")]
                    for dt in detail_texts:
                        b_match = re.search(r"(\d+)\s*quarto", dt, re.IGNORECASE)
                        if b_match:
                            bedrooms = int(b_match.group(1))

                    p_type = self._classify_property_type(title)

                    amenities = []
                    if has_pool:
                        amenities.append("Piscina")
                    if has_bbq:
                        amenities.append("Churrasqueira")
                    if allows_pets:
                        amenities.append("Pet Friendly")
                    if "wi-fi" in card_text or "wifi" in card_text:
                        amenities.append("Wi-Fi")

                    results.append(
                        ScrapedProperty(
                            platform=self.platform_code,
                            external_id=str(ext_id),
                            title=title,
                            url=href,
                            city=city.title(),
                            state=state_code.upper(),
                            property_type=p_type,
                            daily_rate=daily_rate,
                            cleaning_fee=120.0,
                            service_fee=0.0,
                            max_guests=guests if guests > 1 else 12,
                            bedrooms=bedrooms,
                            bathrooms=max(1, bedrooms - 1),
                            has_pool=has_pool,
                            has_bbq=has_bbq,
                            allows_pets=allows_pets,
                            amenities=amenities,
                            images=[img_url] if img_url else [],
                            rating=None,
                            reviews_count=0,
                        )
                    )
                except Exception as e:
                    logger.debug(f"Erro ao processar card OLX: {e}")

        return results
