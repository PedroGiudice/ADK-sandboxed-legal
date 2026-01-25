"""
TJSP (Tribunal de Justica de Sao Paulo) Scraper.

Scraper para o portal de jurisprudencia do TJSP (e-SAJ).
URL: https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do

O TJSP possui o maior volume de decisoes estaduais do Brasil
e oferece acesso gratuito sem cadastro.
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


class TJSPScraper(BaseScraper):
    """
    Scraper para jurisprudencia do Tribunal de Justica de Sao Paulo.

    Features:
    - Busca por texto livre na ementa e inteiro teor
    - Filtros por classe, comarca, relator
    - Acesso ao inteiro teor dos acordaos
    - Banco de Sentencas (1o grau)

    Usage:
        async with TJSPScraper() as scraper:
            results = await scraper.search("dano moral contratual")
            for r in results:
                print(f"{r.numero_processo}: {r.title}")
    """

    @property
    def tribunal_name(self) -> str:
        return "TJSP"

    @property
    def tribunal_full_name(self) -> str:
        return "Tribunal de Justica de Sao Paulo"

    @property
    def base_url(self) -> str:
        return "https://esaj.tjsp.jus.br"

    @property
    def search_url(self) -> str:
        return f"{self.base_url}/cjsg/resultadoCompleta.do"

    @property
    def form_url(self) -> str:
        return f"{self.base_url}/cjsg/consultaCompleta.do"

    async def _init_session(self) -> None:
        """Initialize session by visiting the form page first."""
        try:
            await self._fetch_page(self.form_url)
            logger.debug("Session initialized with TJSP cookies")
        except Exception as e:
            logger.warning(f"Could not initialize session: {e}")

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """
        Search TJSP jurisprudence.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        logger.info(f"TJSP search: '{query}' (max: {max_results})")

        # Initialize session first to get cookies
        await self._init_session()

        # TJSP e-SAJ uses these field names (discovered from form HTML)
        # The form has both 'dados.buscaEmenta' and 'dados.buscaInteiroTeor'
        form_data = {
            "dados.buscaEmenta": query,
            "dados.pesquisarEmentas": "true",
            "dados.buscaInteiroTeor": "",
            "dados.pesquisarInteiroTeor": "false",
            "dados.nuProcOrigem": "",
            "dados.nuRegistro": "",
            "dados.dtJulgamentoInicio": "",
            "dados.dtJulgamentoFim": "",
            "dados.dtPublicacaoInicio": "",
            "dados.dtPublicacaoFim": "",
            "contadorag498": "0",
            "contadoragali498": "0",
        }

        try:
            html = await self._post_page(self.search_url, data=form_data)
            return self._parse_results(html, max_results)

        except ScraperError as e:
            logger.error(f"TJSP search failed: {e}")
            return []

    def _parse_results(self, html: str, max_results: int) -> list[SearchResult]:
        """Parse TJSP search results HTML."""
        soup = self._parse_html(html)
        results: list[SearchResult] = []

        # TJSP results are in table rows with class 'fundocinza1' or 'fundocinza2'
        # Or in divs with class 'ementaClass'
        selectors = [
            "tr.fundocinza1",
            "tr.fundocinza2",
            "div.ementaClass",
            "div.esajResultado",
            "table.resultadoLinha tr",
        ]

        result_elements: list[Tag] = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                result_elements.extend(elements)
                logger.debug(f"Found {len(elements)} results with selector: {selector}")

        if not result_elements:
            # Try to find any table rows with data
            tables = soup.select("table")
            for table in tables:
                rows = table.select("tr")
                if len(rows) > 1:  # Has data rows
                    result_elements.extend(rows[1:])  # Skip header
                    break

        if not result_elements:
            logger.warning("No results found with known selectors")
            # Save HTML for debugging
            with open("debug_tjsp_response.html", "w") as f:
                f.write(html)
            logger.debug("Saved response to debug_tjsp_response.html")
            return []

        for element in result_elements[:max_results]:
            try:
                result = self._parse_single_result(element)
                if result:
                    results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse result: {e}")
                continue

        logger.info(f"Parsed {len(results)} results from TJSP")
        return results

    def _parse_single_result(self, element: Tag) -> Optional[SearchResult]:
        """Parse a single search result element."""
        text = element.get_text()

        # Extract process number (TJSP format)
        # Format: 1234567-89.2020.8.26.0100
        numero = None
        numero_patterns = [
            r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",  # CNJ format
            r"(\d{4}\.\d{2}\.\d{6}-\d)",  # Old format
            r"Processo:\s*([^\s]+)",
        ]

        for pattern in numero_patterns:
            match = re.search(pattern, text)
            if match:
                numero = match.group(1)
                break

        # Extract ementa/title
        ementa_el = element.select_one("td.ementaClass, .ementaClass, td:nth-child(2)")
        title = ""
        if ementa_el:
            title = self._clean_text(ementa_el.get_text())
        else:
            title = self._clean_text(text[:500])

        if not title or len(title) < 20:
            return None

        # Extract URL
        link = element.select_one("a[href*='acordao'], a[href*='documento'], a")
        url = ""
        if link and link.get("href"):
            href = link["href"]
            if href.startswith("/"):
                url = f"{self.base_url}{href}"
            elif href.startswith("http"):
                url = href
            else:
                url = f"{self.base_url}/cjsg/{href}"
        else:
            # Use search URL as fallback
            url = f"{self.search_url}?processo={numero or ''}"

        # Extract relator
        relator = None
        relator_patterns = [
            r"Relator(?:\(a\))?[:\s]+([^;,\n]+)",
            r"Des(?:embargador)?\.?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        for pattern in relator_patterns:
            relator_match = re.search(pattern, text)
            if relator_match:
                relator = self._clean_text(relator_match.group(1))
                break

        # Extract date
        data = None
        data_patterns = [
            r"Data do julgamento[:\s]+(\d{2}/\d{2}/\d{4})",
            r"Julgamento[:\s]+(\d{2}/\d{2}/\d{4})",
            r"(\d{2}/\d{2}/\d{4})",
        ]
        for pattern in data_patterns:
            data_match = re.search(pattern, text)
            if data_match:
                data = data_match.group(1)
                break

        # Extract orgao julgador (Camara)
        classe = None
        classe_match = re.search(
            r"(\d+[aao]?\s*C[aâ]mara\s*(?:de\s*)?(?:Direito\s*)?(?:Privado|Criminal|P[uú]blico)?)",
            text,
            re.IGNORECASE,
        )
        if classe_match:
            classe = self._clean_text(classe_match.group(1))

        return SearchResult(
            url=url,
            title=title[:500],
            snippet=title[:200],
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
            html = await self._fetch_page(url)
            soup = self._parse_html(html)

            # Try multiple selectors for full text
            selectors = [
                "#integra",
                ".integra",
                ".inteiroTeor",
                "#conteudo",
                ".conteudo",
                "#txtEmenta",
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())

            return None

        except Exception as e:
            logger.error(f"Failed to get full text from {url}: {e}")
            return None


# =============================================================================
# STANDALONE TEST
# =============================================================================

async def _test_tjsp_scraper():
    """Test the TJSP scraper with a real query."""
    import asyncio

    print("Testing TJSP Scraper...")

    async with TJSPScraper() as scraper:
        results = await scraper.search("dano moral contratual", max_results=5)

        print(f"\nFound {len(results)} results:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r.numero_processo or 'N/A'}")
            print(f"   Title: {r.title[:100]}...")
            print(f"   Relator: {r.relator}")
            print(f"   Data: {r.data_julgamento}")
            print(f"   Classe: {r.classe}")
            print(f"   URL: {r.url[:80]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_test_tjsp_scraper())
