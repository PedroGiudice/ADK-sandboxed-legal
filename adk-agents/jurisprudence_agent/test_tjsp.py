#!/usr/bin/env python3
"""
Quick test script for the TJSP scraper.
"""

import asyncio
import logging
import re
from typing import Optional
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup, Tag

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""
    url: str
    title: str
    snippet: str
    tribunal: str
    numero_processo: Optional[str] = None
    data_julgamento: Optional[str] = None
    relator: Optional[str] = None
    classe: Optional[str] = None


class TJSPScraperTest:
    """Simplified TJSP scraper for testing."""

    BASE_URL = "https://esaj.tjsp.jus.br"
    FORM_URL = f"{BASE_URL}/cjsg/consultaCompleta.do"
    SEARCH_URL = f"{BASE_URL}/cjsg/resultadoCompleta.do"

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
        "Referer": "https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do",
    }

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.DEFAULT_HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    async def _init_session(self):
        """Visit form page first to get session cookies."""
        try:
            response = await self.client.get(self.FORM_URL)
            logger.info(f"Session init: status={response.status_code}")
        except Exception as e:
            logger.warning(f"Could not init session: {e}")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search TJSP jurisprudence."""
        logger.info(f"Searching TJSP: '{query}'")

        # Initialize session first
        await self._init_session()

        # TJSP e-SAJ uses these field names (from form HTML analysis)
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
            response = await self.client.post(self.SEARCH_URL, data=form_data)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response length: {len(response.text)} chars")

            if response.status_code != 200:
                logger.error(f"Unexpected status: {response.status_code}")
                return []

            return self._parse_results(response.text, max_results)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return []

    def _parse_results(self, html: str, max_results: int) -> list[SearchResult]:
        """Parse search results HTML."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Save HTML for debugging
        with open("debug_tjsp_response.html", "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("Saved response to debug_tjsp_response.html")

        # Try finding results in table
        # TJSP typically uses tables with alternating row colors
        tables = soup.select("table")
        logger.info(f"Found {len(tables)} tables")

        for table in tables:
            rows = table.select("tr")
            if len(rows) > 1:
                logger.info(f"Table with {len(rows)} rows")

        # Look for specific TJSP patterns
        # The results often contain "Registro:" or "Processo:" labels
        all_text = soup.get_text()

        # Find all process numbers
        processo_matches = re.findall(
            r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
            all_text
        )
        logger.info(f"Found {len(processo_matches)} process numbers: {processo_matches[:5]}")

        # Find all acordaos by looking for divs/trs with ementa content
        ementa_elements = soup.select("td[class*='ementa'], div[class*='ementa'], .ementaClass, .ementaClass2")
        logger.info(f"Found {len(ementa_elements)} ementa elements")

        # Alternative: look for divs that contain "EMENTA"
        all_divs = soup.find_all(["div", "td"])
        for div in all_divs[:20]:  # Check first 20
            text = div.get_text()[:100]
            if "EMENTA" in text or "ACORDAO" in text.upper():
                logger.debug(f"Found potential result div: {text[:50]}...")

        # Parse using rows
        result_rows = soup.select("tr.fundocinza1, tr.fundocinza2, tr[bgcolor]")
        if not result_rows:
            # Try alternative selector
            result_rows = soup.select("table tr")[1:]  # Skip headers

        logger.info(f"Processing {len(result_rows)} potential result rows")

        for row in result_rows[:max_results]:
            result = self._parse_row(row)
            if result:
                results.append(result)

        # If no results, try parsing by processo numbers found
        if not results and processo_matches:
            logger.info("Falling back to processo number extraction")
            for i, proc in enumerate(processo_matches[:max_results]):
                results.append(SearchResult(
                    url=f"{self.BASE_URL}/cjsg/getArquivo.do?cdAcordao=0&cdForo=0",
                    title=f"Processo {proc} (detalhes na URL)",
                    snippet="Ementa nao extraida automaticamente",
                    tribunal="TJSP",
                    numero_processo=proc,
                ))

        return results

    def _parse_row(self, row: Tag) -> Optional[SearchResult]:
        """Parse a single result row."""
        text = row.get_text()

        # Must have substantial content
        if len(text.strip()) < 50:
            return None

        # Extract process number
        numero = None
        match = re.search(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", text)
        if match:
            numero = match.group(1)

        # Extract title/ementa
        cells = row.select("td")
        title = ""
        for cell in cells:
            cell_text = cell.get_text().strip()
            if len(cell_text) > len(title):
                title = cell_text

        title = " ".join(title.split())[:500]

        if not title or len(title) < 30:
            return None

        # Extract URL
        link = row.select_one("a[href]")
        url = link["href"] if link else self.SEARCH_URL
        if url.startswith("/"):
            url = f"{self.BASE_URL}{url}"

        # Extract relator
        relator_match = re.search(r"Relator[:\s]+([^;,\n]+)", text)
        relator = relator_match.group(1).strip() if relator_match else None

        # Extract date
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        data = date_match.group(1) if date_match else None

        return SearchResult(
            url=url,
            title=title,
            snippet=title[:200],
            tribunal="TJSP",
            numero_processo=numero,
            data_julgamento=data,
            relator=relator,
        )


async def main():
    """Test the TJSP scraper."""
    query = "dano moral contratual"
    print(f"\nTesting TJSP Scraper with query: '{query}'")
    print("=" * 60)

    async with TJSPScraperTest() as scraper:
        results = await scraper.search(query, max_results=5)

        print(f"\nFound {len(results)} results:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r.numero_processo or 'N/A'}")
            print(f"   Title: {r.title[:100]}...")
            print(f"   Relator: {r.relator}")
            print(f"   Data: {r.data_julgamento}")
            print(f"   URL: {r.url[:80]}...")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
