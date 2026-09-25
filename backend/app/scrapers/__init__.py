from app.scrapers.base import BaseScraper, ScrapedProperty, ScraperUnavailableError
from app.scrapers.olx import OLXScraper
from app.scrapers.temporadalivre import TemporadaLivreScraper

__all__ = ["BaseScraper", "ScrapedProperty", "ScraperUnavailableError", "TemporadaLivreScraper", "OLXScraper"]
