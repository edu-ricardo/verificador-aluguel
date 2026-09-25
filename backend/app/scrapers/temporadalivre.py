import re
import unicodedata
from datetime import date
from typing import List, Optional

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ScrapedProperty, ScraperUnavailableError, logger

BRAZIL_STATES = {
    "AC": "acre",
    "AL": "alagoas",
    "AP": "amapa",
    "AM": "amazonas",
    "BA": "bahia",
    "CE": "ceara",
    "DF": "distrito-federal",
    "ES": "espirito-santo",
    "GO": "goias",
    "MA": "maranhao",
    "MT": "mato-grosso",
    "MS": "mato-grosso-do-sul",
    "MG": "minas-gerais",
    "PA": "para",
    "PB": "paraiba",
    "PR": "parana",
    "PE": "pernambuco",
    "PI": "piaui",
    "RJ": "rio-de-janeiro",
    "RN": "rio-grande-do-norte",
    "RS": "rio-grande-do-sul",
    "RO": "rondonia",
    "RR": "roraima",
    "SC": "santa-catarina",
    "SP": "sao-paulo",
    "SE": "sergipe",
    "TO": "tocantins",
}


class TemporadaLivreScraper(BaseScraper):
    platform_name = "TemporadaLivre"
    platform_code = "temporadalivre"
    base_url = "https://www.temporadalivre.com"

    def _slugify(self, text: str) -> str:
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
        text = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "-", text)

    def _get_state_slug(self, state: Optional[str]) -> str:
        if not state:
            return "sao-paulo"
        st = state.strip().upper()
        if st in BRAZIL_STATES:
            return BRAZIL_STATES[st]
        slug = self._slugify(state)
        if slug in BRAZIL_STATES.values():
            return slug
        return "sao-paulo"

    def _extract_price(self, text: str) -> float:
        if not text:
            return 0.0
        # Exemplo: "R$ 450", "R$ 1.200,00", "790"
        match = re.search(r"R\$\s*([\d\.,]+)", text)
        if match:
            raw_val = match.group(1).replace(".", "").replace(",", ".")
            try:
                return float(raw_val)
            except ValueError:
                return 0.0
        # Se for apenas o número da diária
        num_match = re.search(r"(\d+[\.,]?\d*)", text)
        if num_match:
            try:
                return float(num_match.group(1).replace(",", "."))
            except ValueError:
                return 0.0
        return 0.0

    async def search(
        self,
        city: str,
        state: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        guests: int = 1,
        property_type: Optional[str] = None,
    ) -> List[ScrapedProperty]:
        city_slug = self._slugify(city)
        state_slug = self._get_state_slug(state)

        # URL canônica do TemporadaLivre por cidade
        url = f"{self.base_url}/aluguel-temporada/brasil/{state_slug}/{city_slug}"

        params = {}
        if guests > 1:
            # "pessoas-min" = capacidade mínima; "pessoas-max" limitaria a imóveis MENORES que o grupo
            params["pessoas-min"] = guests
        if check_in and check_out:
            params["data_inicio"] = check_in.strftime("%d/%m/%Y")
            params["data_fim"] = check_out.strftime("%d/%m/%Y")

        html = await self.fetch_html(url, params=params)

        # Fallback de busca se a URL direta não retornar página válida
        if not html:
            search_url = f"{self.base_url}/aluguel-temporada"
            html = await self.fetch_html(search_url, params={"search": city})

        if not html:
            raise ScraperUnavailableError(f"{self.platform_name} não respondeu para {city}")

        results: List[ScrapedProperty] = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            # Encontra cartões de imóveis reais
            cards = soup.select("a.show-details, a[href*='/aluguel-temporada/brasil/']")
            seen_ids = set()

            for card in cards:
                try:
                    href = card.get("href", "")
                    if not href or not re.search(r"/\d{4,}-", href):
                        continue

                    ext_id_match = re.search(r"/(\d{4,})-", href)
                    ext_id = ext_id_match.group(1) if ext_id_match else card.get("data-id", href)
                    if ext_id in seen_ids:
                        continue
                    seen_ids.add(ext_id)

                    full_url = href if href.startswith("http") else f"{self.base_url}{href}"

                    # Título
                    title_elem = card.select_one("span.title, .title, h2, h3")
                    title = title_elem.get_text(strip=True) if title_elem else "Imóvel de Temporada"

                    # Preço da diária
                    price_elem = card.select_one("span[data-behavior='rate'], span.price, .price")
                    daily_rate = 0.0
                    if price_elem:
                        daily_rate = self._extract_price(price_elem.get_text(strip=True))
                    # Sem diária não há o que comparar — não inventamos um valor
                    if daily_rate <= 0:
                        continue

                    # Foto real do anúncio
                    img_elem = card.select_one("div.image img, img")
                    img_url = ""
                    if img_elem:
                        img_url = img_elem.get("src") or img_elem.get("data-src") or ""

                    # Capacidade de hóspedes e quartos
                    max_g = guests if guests > 1 else 10
                    bedrooms = 3
                    numbers_elem = card.select_one("div.numbers")
                    if numbers_elem:
                        num_text = numbers_elem.get_text()
                        g_match = re.search(r"(\d+)\s*Pessoas", num_text, re.IGNORECASE)
                        if g_match:
                            max_g = int(g_match.group(1))
                        b_match = re.search(r"(\d+)\s*Quartos", num_text, re.IGNORECASE)
                        if b_match:
                            bedrooms = int(b_match.group(1))

                    # Bairro / Localização
                    neighborhood = None
                    loc_elem = card.select_one("div.location")
                    if loc_elem:
                        loc_parts = loc_elem.get_text(strip=True).split("/")
                        if len(loc_parts) > 1:
                            neighborhood = loc_parts[1].strip()

                    card_text = card.get_text().lower()
                    has_pool = "piscina" in card_text or "piscina" in title.lower()
                    allows_pets = "pet" in card_text or "animais" in card_text
                    has_bbq = "churrasqueira" in card_text or "churras" in card_text or "gourmet" in card_text

                    # Tipo de propriedade
                    p_type = "chacara"
                    if "sitio" in title.lower() or "sítio" in title.lower():
                        p_type = "sitio"
                    elif "apartamento" in title.lower() or "apto" in title.lower():
                        p_type = "casa"
                    elif "casa" in title.lower():
                        p_type = "casa"

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
                            url=full_url,
                            city=city.title(),
                            state=(state or "SP").upper(),
                            property_type=p_type,
                            neighborhood=neighborhood,
                            daily_rate=daily_rate,
                            cleaning_fee=150.0,
                            service_fee=0.0,
                            max_guests=max_g,
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
                    logger.debug(f"Erro ao processar card TemporadaLivre: {e}")

        return results
