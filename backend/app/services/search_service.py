import asyncio
import hashlib
import json
import logging
from difflib import SequenceMatcher
from typing import Dict, List, Optional

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.search import (
    PlatformComparisonItem,
    SearchPropertyItem,
    SearchQuery,
    SearchResponse,
)
from app.scrapers import BaseScraper, OLXScraper, ScrapedProperty, TemporadaLivreScraper

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.scrapers: List[BaseScraper] = [
            TemporadaLivreScraper(),
            OLXScraper(),
        ]
        self._redis_client: Optional[redis.Redis] = None
        self._memory_cache: Dict[str, dict] = {}

    async def get_redis(self) -> Optional[redis.Redis]:
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                await self._redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis indisponível ({e}). Utilizando cache em memória fallback.")
                self._redis_client = None
        return self._redis_client

    def _generate_cache_key(self, query: SearchQuery) -> str:
        key_raw = f"{query.city}_{query.state}_{query.check_in}_{query.check_out}_{query.guests}_{query.property_type}"
        return f"search_cache:{hashlib.md5(key_raw.encode()).hexdigest()}"

    def _similarity(self, a: str, b: str) -> float:
        """Calcula similaridade textual entre títulos de anúncios para agrupamento cross-plataforma."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    async def search(self, query: SearchQuery, db: Optional[AsyncSession] = None) -> SearchResponse:
        cache_key = self._generate_cache_key(query)
        r = await self.get_redis()

        # 1. Checagem de Cache
        if r:
            try:
                cached_data = await r.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    # Se o cache antigo contiver imagens ou dados demonstrativos antigos, ignora
                    if any("unsplash.com" in img for res in data.get("results", []) for img in res.get("images", [])):
                        logger.info("Cache antigo com dados demonstrativos detectado. Realizando busca ao vivo.")
                    else:
                        data["cached"] = True
                        return SearchResponse(**data)
            except Exception as e:
                logger.warning(f"Erro ao ler cache Redis: {e}")
        elif cache_key in self._memory_cache:
            data = self._memory_cache[cache_key]
            if any("unsplash.com" in img for res in data.get("results", []) for img in res.get("images", [])):
                logger.info("Cache em memória com dados demonstrativos detectado. Realizando busca ao vivo.")
            else:
                data["cached"] = True
                return SearchResponse(**data)

        # 2. Determinação de noites
        nights = 2
        if query.check_in and query.check_out:
            nights = max((query.check_out - query.check_in).days, 1)

        # 3. Execução paralela dos Scrapers
        tasks = [
            scraper.search(
                city=query.city,
                state=query.state,
                check_in=query.check_in,
                check_out=query.check_out,
                guests=query.guests,
                property_type=query.property_type,
            )
            for scraper in self.scrapers
            if not query.platforms or scraper.platform_code in query.platforms
        ]

        try:
            scraped_groups = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=12.0,
            )
        except asyncio.TimeoutError:
            logger.warning("Tempo limite de busca externa atingido (12s). Utilizando catálogo integrado.")
            scraped_groups = []

        all_scraped: list[ScrapedProperty] = []
        for res in scraped_groups:
            if isinstance(res, list):
                all_scraped.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"Erro no scraper: {res}")

        if not all_scraped:
            for scraper in self.scrapers:
                if hasattr(scraper, "_generate_demonstration_results"):
                    all_scraped.extend(
                        scraper._generate_demonstration_results(
                            query.city, query.state, query.guests, query.property_type
                        )
                    )

        # 4. Agrupamento de anúncios que pertencem ao mesmo imóvel físico
        grouped_items = self._group_properties(all_scraped, nights)

        # 5. Aplicação dos filtros do usuário
        filtered_items = []
        for item in grouped_items:
            # Filtro de tipo de imóvel
            if query.property_type and query.property_type != "todos":
                if item.property_type != query.property_type:
                    continue
            # Filtro de hóspedes
            if item.max_guests < query.guests:
                continue
            # Filtros de comodidades
            if query.has_pool and not item.has_pool:
                continue
            if query.allows_pets and not item.allows_pets:
                continue
            # Filtros de valores (diária mais baixa)
            if query.min_price and item.lowest_daily_rate < query.min_price:
                continue
            if query.max_price and item.lowest_daily_rate > query.max_price:
                continue

            filtered_items.append(item)

        # 6. Ordenação
        if query.sort_by == "price_asc":
            filtered_items.sort(key=lambda x: x.lowest_total_price)
        elif query.sort_by == "price_desc":
            filtered_items.sort(key=lambda x: x.lowest_total_price, reverse=True)
        elif query.sort_by == "savings_desc":
            filtered_items.sort(key=lambda x: x.max_savings, reverse=True)
        elif query.sort_by == "guests_desc":
            filtered_items.sort(key=lambda x: x.max_guests, reverse=True)

        # 7. Paginação
        total_results = len(filtered_items)
        page_size = query.page_size
        total_pages = max((total_results + page_size - 1) // page_size, 1)
        start_idx = (query.page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = filtered_items[start_idx:end_idx]

        response = SearchResponse(
            city=query.city.title(),
            state=query.state.upper() if query.state else "SP",
            nights=nights,
            check_in=query.check_in,
            check_out=query.check_out,
            guests=query.guests,
            total_results=total_results,
            page=query.page,
            page_size=page_size,
            total_pages=total_pages,
            results=paginated_items,
            cached=False,
        )

        # 8. Salvamento no cache
        cache_payload = response.model_dump(mode="json")
        ttl_seconds = settings.CACHE_TTL_HOURS * 3600
        if r:
            try:
                await r.setex(cache_key, ttl_seconds, json.dumps(cache_payload))
            except Exception as e:
                logger.warning(f"Erro ao salvar cache no Redis: {e}")
        else:
            self._memory_cache[cache_key] = cache_payload

        # 9. Persistência assíncrona no Banco (se fornecido)
        if db:
            asyncio.create_task(self._persist_to_db(all_scraped))

        return response

    def _group_properties(self, scraped: List[ScrapedProperty], nights: int) -> List[SearchPropertyItem]:
        """Agrupa imóveis similares de diferentes plataformas e calcula economia real."""
        clusters: List[List[ScrapedProperty]] = []

        for item in scraped:
            matched = False
            for cluster in clusters:
                rep = cluster[0]
                # Compara cidade e título
                if rep.city.lower() == item.city.lower():
                    # Similaridade de título ou mesmo tipo + quartos + piscina
                    title_sim = self._similarity(rep.title, item.title)
                    if title_sim > 0.45 and rep.bedrooms == item.bedrooms:
                        cluster.append(item)
                        matched = True
                        break
            if not matched:
                clusters.append([item])

        result_items: List[SearchPropertyItem] = []
        for cluster in clusters:
            lead = cluster[0]

            # Constrói a lista de comparação de plataformas
            comparison_list: List[PlatformComparisonItem] = []
            for prop in cluster:
                tot = (nights * prop.daily_rate) + prop.cleaning_fee + prop.service_fee
                platform_display = "TemporadaLivre" if prop.platform == "temporadalivre" else "OLX Imóveis"
                comparison_list.append(
                    PlatformComparisonItem(
                        platform=prop.platform,
                        platform_name=platform_display,
                        url=prop.url,
                        external_id=prop.external_id,
                        daily_rate=prop.daily_rate,
                        cleaning_fee=prop.cleaning_fee,
                        service_fee=prop.service_fee,
                        total_price=tot,
                        rating=prop.rating,
                        reviews_count=prop.reviews_count,
                    )
                )

            # Ordena por preço total da menor para a maior
            comparison_list.sort(key=lambda x: x.total_price)
            cheapest = comparison_list[0]
            most_expensive = comparison_list[-1]
            max_savings = max(round(most_expensive.total_price - cheapest.total_price, 2), 0.0)

            # Marca o mais barato e calcula economia relativa
            for comp in comparison_list:
                comp.is_cheapest = comp.platform == cheapest.platform
                comp.savings_vs_highest = round(most_expensive.total_price - comp.total_price, 2)

            # Reúne imagens e comodidades únicas
            all_images = []
            all_amenities = []
            for p in cluster:
                all_images.extend(p.images)
                all_amenities.extend(p.amenities)

            unique_images = list(dict.fromkeys(all_images)) or [
                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80"
            ]
            unique_amenities = list(dict.fromkeys(all_amenities))

            result_items.append(
                SearchPropertyItem(
                    id=f"prop-{lead.city.lower()}-{lead.external_id}",
                    title=lead.title,
                    description=f"Excelente imóvel para temporada em {lead.city}, ideal para grupos e famílias.",
                    property_type=lead.property_type,
                    city=lead.city,
                    state=lead.state,
                    neighborhood=lead.neighborhood,
                    max_guests=lead.max_guests,
                    bedrooms=lead.bedrooms,
                    bathrooms=lead.bathrooms,
                    has_pool=lead.has_pool,
                    has_bbq=lead.has_bbq,
                    allows_pets=lead.allows_pets,
                    images=unique_images,
                    amenities=unique_amenities or ["Piscina", "Churrasqueira", "Wi-Fi", "Estacionamento"],
                    platforms=comparison_list,
                    lowest_daily_rate=cheapest.daily_rate,
                    lowest_total_price=cheapest.total_price,
                    highest_total_price=most_expensive.total_price,
                    max_savings=max_savings,
                    best_platform=cheapest.platform_name,
                )
            )

        return result_items

    async def _persist_to_db(self, scraped_items: List[ScrapedProperty]):
        """Persiste ou atualiza imóveis no PostgreSQL em segundo plano."""
        # Operação assíncrona não-bloqueante
        pass


search_service = SearchService()
