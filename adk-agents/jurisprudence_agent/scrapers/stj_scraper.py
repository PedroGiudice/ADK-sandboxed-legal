"""
STJ (Superior Tribunal de Justica) Scraper.

Scraper para o portal de jurisprudencia do STJ.
URL: https://scon.stj.jus.br/SCON/

O STJ possui uma das interfaces de busca mais completas,
suportando operadores booleanos e filtros avancados.
"""

import re
import urllib.parse
from typing import Optional
import logging

from bs4 import BeautifulSoup, Tag

# Handle both package and standalone imports
try:
    from .base import BaseScraper, ScraperError, ParseError
    from ..models import SearchResult
except ImportError:
    from base import BaseScraper, ScraperError, ParseError
    from models import SearchResult


logger = logging.getLogger(__name__)


class STJScraper(BaseScraper):
    """
    Scraper para jurisprudencia do Superior Tribunal de Justica.

    Features:
    - Busca por texto livre com operadores booleanos
    - Filtros por relator, classe processual, orgao julgador
    - Acesso ao inteiro teor dos acordaos

    Usage:
        async with STJScraper() as scraper:
            results = await scraper.search("dano moral contratual")
            for r in results:
                print(f"{r.numero_processo}: {r.title}")
    """

    # Headers mais realistas para evitar bloqueio
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override default headers
        self.user_agent = self.DEFAULT_HEADERS["User-Agent"]

    @property
    def tribunal_name(self) -> str:
        return "STJ"

    @property
    def tribunal_full_name(self) -> str:
        return "Superior Tribunal de Justica"

    @property
    def base_url(self) -> str:
        return "https://scon.stj.jus.br"

    @property
    def search_url(self) -> str:
        return f"{self.base_url}/SCON/pesquisar.jsp"

    async def _init_session(self) -> None:
        """Initialize session by visiting the main page first."""
        # Visit main page to get cookies
        try:
            await self._fetch_page(
                f"{self.base_url}/SCON/",
                headers=self.DEFAULT_HEADERS,
            )
            logger.debug("Session initialized with STJ cookies")
        except Exception as e:
            logger.warning(f"Could not initialize session: {e}")

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """
        Search STJ jurisprudence.

        Args:
            query: Search query (supports boolean operators: E, OU, NAO)
            max_results: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        logger.info(f"STJ search: '{query}' (max: {max_results})")

        # Initialize session first
        await self._init_session()

        # Build search URL with query parameters
        # STJ uses 'pesquisaLivre' for free text search
        params = {
            "pesquisaLivre": query,
            "b": "ACOR",  # Base: Acordaos
            "p": "true",  # Pesquisa
            "l": str(max_results),  # Limite
            "i": "1",  # Inicio
        }

        search_url = f"{self.search_url}?{urllib.parse.urlencode(params)}"

        try:
            html = await self._fetch_page(
                search_url,
                headers=self.DEFAULT_HEADERS,
            )
            return self._parse_results(html, max_results)

        except ScraperError as e:
            logger.error(f"STJ search failed: {e}")
            # Try alternative approach with POST
            return await self._search_via_post(query, max_results)

    async def _search_via_post(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        """Alternative search using POST request."""
        logger.info("Trying POST search method")

        form_data = {
            "pesquisaLivre": query,
            "b": "ACOR",
            "p": "true",
            "l": str(max_results),
            "i": "1",
            "operador": "e",  # Default AND operator
        }

        try:
            html = await self._post_page(
                self.search_url,
                data=form_data,
                headers=self.DEFAULT_HEADERS,
            )
            return self._parse_results(html, max_results)

        except ScraperError as e:
            logger.error(f"STJ POST search also failed: {e}")
            return []

    def _parse_results(self, html: str, max_results: int) -> list[SearchResult]:
        """
        Parse STJ search results HTML.

        The STJ results page typically contains:
        - divs with class 'documentoTexto' for each result
        - Process number, relator, ementa, etc. in specific positions
        """
        soup = self._parse_html(html)
        results: list[SearchResult] = []

        # Try multiple selectors as STJ may have different layouts
        selectors = [
            "div.documentoTexto",
            "div.documento",
            "div.resultadoPesquisa",
            "tr.fundocinza1, tr.fundocinza2",  # Table-based results
        ]

        result_elements: list[Tag] = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                result_elements = elements
                logger.debug(f"Found {len(elements)} results with selector: {selector}")
                break

        if not result_elements:
            # Log HTML snippet for debugging
            logger.warning("No results found with known selectors")
            logger.debug(f"HTML snippet: {html[:2000]}...")
            return []

        for element in result_elements[:max_results]:
            try:
                result = self._parse_single_result(element)
                if result:
                    results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse result: {e}")
                continue

        logger.info(f"Parsed {len(results)} results from STJ")
        return results

    def _parse_single_result(self, element: Tag) -> Optional[SearchResult]:
        """Parse a single search result element."""
        # Try to extract process number
        numero = None
        numero_patterns = [
            r"(REsp|AgInt|AgRg|HC|RHC|MS|RMS|EREsp)\s*[\d\./-]+",
            r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}",  # CNJ format
        ]

        text = element.get_text()
        for pattern in numero_patterns:
            match = re.search(pattern, text)
            if match:
                numero = match.group()
                break

        # Extract ementa/title
        ementa_el = element.select_one(
            ".ementa, .ementaTexto, [class*='ementa']"
        )
        title = ""
        if ementa_el:
            title = self._clean_text(ementa_el.get_text())
        else:
            # Fallback: use first substantial text block
            title = self._clean_text(text[:500])

        if not title:
            return None

        # Extract URL
        link = element.select_one("a[href*='documento'], a[href*='acordao']")
        url = ""
        if link and link.get("href"):
            href = link["href"]
            if href.startswith("/"):
                url = f"{self.base_url}{href}"
            elif href.startswith("http"):
                url = href
            else:
                url = f"{self.base_url}/SCON/{href}"
        else:
            # Generate a search URL as fallback
            url = f"{self.search_url}?pesquisaLivre={urllib.parse.quote(numero or title[:50])}"

        # Extract relator
        relator = None
        relator_el = element.select_one(".relator, [class*='relator']")
        if relator_el:
            relator = self._clean_text(relator_el.get_text())
        else:
            # Try regex
            relator_match = re.search(
                r"(?:Relator|Min\.|Ministro)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                text,
            )
            if relator_match:
                relator = relator_match.group(1)

        # Extract date
        data = None
        data_match = re.search(
            r"(\d{2}/\d{2}/\d{4})",
            text,
        )
        if data_match:
            data = data_match.group(1)

        # Extract class (REsp, HC, etc)
        classe = None
        if numero:
            classe_match = re.match(r"([A-Za-z]+)", numero)
            if classe_match:
                classe = classe_match.group(1).upper()

        return SearchResult(
            url=url,
            title=title[:500],  # Limit title length
            snippet=title[:200],  # Short snippet
            tribunal=self.tribunal_name,
            numero_processo=numero,
            data_julgamento=data,
            relator=relator,
            classe=classe,
        )

    async def get_full_text(self, url: str) -> Optional[str]:
        """
        Fetch full text of a decision.

        Args:
            url: URL to the decision page

        Returns:
            Full text content or None
        """
        try:
            html = await self._fetch_page(url, headers=self.DEFAULT_HEADERS)
            soup = self._parse_html(html)

            # Try multiple selectors for full text
            selectors = [
                "#integra",
                ".integra",
                ".inteiroTeor",
                ".documentoInteiro",
                "#conteudo",
                ".conteudo",
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())

            # Fallback: get body content
            body = soup.select_one("body")
            if body:
                return self._clean_text(body.get_text())[:10000]

            return None

        except Exception as e:
            logger.error(f"Failed to get full text from {url}: {e}")
            return None


# =============================================================================
# STANDALONE TEST
# =============================================================================

async def _test_stj_scraper():
    """Test the STJ scraper with a real query."""
    import asyncio

    print("Testing STJ Scraper...")

    async with STJScraper() as scraper:
        results = await scraper.search("dano moral contratual", max_results=5)

        print(f"\nFound {len(results)} results:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r.numero_processo or 'N/A'}")
            print(f"   Title: {r.title[:100]}...")
            print(f"   Relator: {r.relator}")
            print(f"   Data: {r.data_julgamento}")
            print(f"   URL: {r.url}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_test_stj_scraper())
