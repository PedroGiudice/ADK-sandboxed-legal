"""
Scrapers modulares por site de tribunal.

NOTA: A maioria dos sites de tribunais tem protecao CAPTCHA ou bloqueia acesso
automatizado. O GoogleCourtsScraper eh uma alternativa pragmatica que usa
Google Search com restricao de sites para alcancar busca em whitelist.

Scrapers disponiveis:
- STJScraper: Tentativa de scraping direto do STJ (pode falhar com 403)
- TJSPScraper: Tentativa de scraping direto do TJSP (tem CAPTCHA)
- GoogleCourtsScraper: Usa Google Search com site: restrictions
"""

from .base import BaseScraper, ScraperError, RateLimitError, ParseError
from .stj_scraper import STJScraper
from .tjsp_scraper import TJSPScraper
from .google_courts_scraper import GoogleCourtsScraper, COURT_DOMAINS
from ..models import SearchResult

__all__ = [
    # Base classes
    "BaseScraper",
    "ScraperError",
    "RateLimitError",
    "ParseError",
    # Scrapers
    "STJScraper",
    "TJSPScraper",
    "GoogleCourtsScraper",
    # Config
    "COURT_DOMAINS",
    # Models
    "SearchResult",
]
