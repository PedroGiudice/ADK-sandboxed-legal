#!/usr/bin/env python3
"""
Quick test script for the STJ scraper.
Run from the jurisprudence_agent directory.
"""

import asyncio
import logging
import sys
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import urllib.parse

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
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


class STJScraperTest:
    """Simplified STJ scraper for testing."""

    BASE_URL = "https://scon.stj.jus.br"
    SEARCH_URL = f"{BASE_URL}/SCON/pesquisar.jsp"

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

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search STJ jurisprudence."""
        logger.info(f"Searching STJ: '{query}'")

        # First visit main page to get cookies
        try:
            await self.client.get(f"{self.BASE_URL}/SCON/")
        except Exception as e:
            logger.warning(f"Could not init session: {e}")

        # Build search URL
        params = {
            "pesquisaLivre": query,
            "b": "ACOR",
            "p": "true",
            "l": str(max_results),
        }
        search_url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"

        try:
            response = await self.client.get(search_url)
            logger.info(f"Response status: {response.status_code}")

            if response.status_code == 403:
                logger.error("Access denied (403) - site is blocking requests")
                return self._mock_results(query)

            response.raise_for_status()
            return self._parse_results(response.text, max_results)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return self._mock_results(query)

    def _parse_results(self, html: str, max_results: int) -> list[SearchResult]:
        """Parse search results HTML."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Log HTML structure for debugging
        logger.debug(f"HTML length: {len(html)}")

        # Try different selectors
        for selector in ["div.documentoTexto", "div.documento", "tr"]:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with '{selector}'")
                for el in elements[:max_results]:
                    result = self._parse_element(el)
                    if result:
                        results.append(result)
                break

        if not results:
            logger.warning("No results parsed - HTML structure may have changed")
            # Save HTML for analysis
            with open("debug_stj_response.html", "w") as f:
                f.write(html)
            logger.info("Saved response to debug_stj_response.html")

        return results

    def _parse_element(self, el: Tag) -> Optional[SearchResult]:
        """Parse a single result element."""
        text = el.get_text()

        # Extract process number
        numero = None
        for pattern in [
            r"(REsp|AgInt|AgRg|HC|RHC|MS|RMS|EREsp)\s*[\d\./-]+",
            r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}",
        ]:
            match = re.search(pattern, text)
            if match:
                numero = match.group()
                break

        # Get title
        title = " ".join(text.split())[:500]
        if not title:
            return None

        # Get URL
        link = el.select_one("a[href]")
        url = link["href"] if link else f"{self.SEARCH_URL}"
        if url.startswith("/"):
            url = f"{self.BASE_URL}{url}"

        # Extract relator
        relator_match = re.search(r"Min\.?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
        relator = relator_match.group(1) if relator_match else None

        # Extract date
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        data = date_match.group(1) if date_match else None

        return SearchResult(
            url=url,
            title=title,
            snippet=title[:200],
            tribunal="STJ",
            numero_processo=numero,
            data_julgamento=data,
            relator=relator,
        )

    def _mock_results(self, query: str) -> list[SearchResult]:
        """Return mock results when real search fails."""
        logger.warning("Using mock results due to access restrictions")
        return [
            SearchResult(
                url="https://scon.stj.jus.br/exemplo",
                title=f"[MOCK] Resultado para: {query}",
                snippet="Resultado simulado - site bloqueou acesso",
                tribunal="STJ",
                numero_processo="REsp 1234567/SP",
                relator="Min. Exemplo",
            )
        ]


async def main():
    """Test the STJ scraper."""
    query = "dano moral contratual"
    print(f"\nTesting STJ Scraper with query: '{query}'")
    print("=" * 60)

    async with STJScraperTest() as scraper:
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
