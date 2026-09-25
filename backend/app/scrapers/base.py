import logging
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

    async def fetch_html(self, url: str, params: Optional[dict] = None) -> Optional[str]:
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=httpx.Timeout(10.0, connect=5.0),
                follow_redirects=True,
            ) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return response.text
                logger.warning(f"[{self.platform_code}] HTTP {response.status_code} para {url}")
                return None
        except Exception as e:
            logger.error(f"[{self.platform_code}] Falha ao requisitar {url}: {e}")
            return None

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
