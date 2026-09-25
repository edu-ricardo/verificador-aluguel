import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ScraperUnavailableError(Exception):
    """O portal não respondeu (bloqueio, timeout ou erro HTTP) — diferente de "nenhum resultado"."""


@dataclass
class ScrapedProperty:
    platform: str
    external_id: str
    title: str
    url: str
    city: str
    state: str
    property_type: str = "chacara"  # chacara, sitio, casa
    neighborhood: Optional[str] = None
    daily_rate: float = 0.0
    cleaning_fee: float = 0.0
    service_fee: float = 0.0
    max_guests: int = 1
    bedrooms: int = 1
    bathrooms: int = 1
    has_pool: bool = False
    has_bbq: bool = False
    allows_pets: bool = False
    amenities: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    rating: Optional[float] = None
    reviews_count: int = 0


class BaseScraper(ABC):
    platform_name: str = ""
    platform_code: str = ""

    def __init__(self):
        self.headers = {
            "User-Agent": settings.SCRAPER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
        }

    async def fetch_html(self, url: str, params: Optional[dict] = None) -> str:
        """Baixa a página; levanta ScraperUnavailableError com o motivo (timeout, DNS, HTTP 403...)."""
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=httpx.Timeout(10.0, connect=5.0),
                follow_redirects=True,
            ) as client:
                response = await client.get(url, params=params)
        except Exception as e:
            # Exceções de timeout do httpx têm str() vazio: o nome da classe é o que diagnostica o problema
            reason = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            logger.error(f"[{self.platform_code}] Falha ao requisitar {url}: {reason}")
            raise ScraperUnavailableError(reason) from e

        if response.status_code != 200:
            logger.warning(f"[{self.platform_code}] HTTP {response.status_code} para {response.url}")
            raise ScraperUnavailableError(f"HTTP {response.status_code}")
        return response.text

    @staticmethod
    def _extract_price(text: str) -> float:
        """Converte "R$ 1.200", "R$ 450,00" ou "790" em float (ponto é separador de milhar)."""
        if not text:
            return 0.0
        match = re.search(r"\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?", text)
        if not match:
            return 0.0
        return float(match.group(0).replace(".", "").replace(",", "."))

    @staticmethod
    def _mentions_pets(text: str) -> bool:
        # Palavra inteira: "pet" como substring casaria "Petrópolis", "carpete", "competição"...
        return re.search(r"\b(pets?|animais|aceita animal)\b", text) is not None

    @staticmethod
    def _classify_property_type(title: str) -> str:
        """chacara | sitio | casa — o padrão é "casa" para não rotular apartamentos/chalés como chácara."""
        t = title.lower()
        if re.search(r"\b(ch[aá]cara|rancho)\b", t):
            return "chacara"
        if re.search(r"\b(s[ií]tio|fazenda)\b", t):
            return "sitio"
        return "casa"

    @abstractmethod
    async def search(
        self,
        city: str,
        state: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        guests: int = 1,
        property_type: Optional[str] = None,
    ) -> List[ScrapedProperty]:
        """Realiza a busca no portal e retorna a lista de propriedades normalizadas."""
        pass
