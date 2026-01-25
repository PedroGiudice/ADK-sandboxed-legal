"""
Google Courts Scraper - Uses Google Search restricted to court domains.

Since Brazilian court websites (STJ, TJSP, TJMG, TJRJ) have CAPTCHA protection
and complex session handling, this scraper uses Google Search with site
restrictions to search within those domains.

This achieves the whitelist goal while actually returning results.
"""

import re
import urllib.parse
from typing import Optional
import logging

import httpx
from bs4 import BeautifulSoup

# Handle both package and standalone imports
try:
    from .base import BaseScraper, ScraperError
    from ..models import SearchResult
except ImportError:
    from base import BaseScraper, ScraperError
    from models import SearchResult


logger = logging.getLogger(__name__)


# Court domains for site-restricted search
COURT_DOMAINS = [
    "stj.jus.br",
    "tjsp.jus.br",
    "tjmg.jus.br",
    "tjrj.jus.br",
    "stf.jus.br",
    "tst.jus.br",
    "trf1.jus.br",
    "trf2.jus.br",
    "trf3.jus.br",
    "trf4.jus.br",
    "trf5.jus.br",
    "cjf.jus.br",
]


class GoogleCourtsScraper(BaseScraper):
    """
    Scraper that uses Google Search restricted to Brazilian court domains.

    This is a pragmatic approach since direct court scraping faces:
    - CAPTCHA protection (TJSP, TJMG)
    - Bot blocking (STJ 403)
    - Complex session handling
    - JavaScript-dependent forms

    Usage:
        async with GoogleCourtsScraper() as scraper:
            results = await scraper.search("dano moral contratual")
    """

    @property
    def tribunal_name(self) -> str:
        return "Google-Courts"

    @property
    def tribunal_full_name(self) -> str:
        return "Google Search (Brazilian Courts)"

    @property
    def base_url(self) -> str:
        return "https://www.google.com"

    @property
    def search_url(self) -> str:
        return f"{self.base_url}/search"

    def _build_site_query(self, query: str, domains: list[str] = None) -> str:
        """
        Build a Google search query restricted to court domains.

        Args:
            query: Search query
            domains: List of domains to search (defaults to COURT_DOMAINS)

        Returns:
            Query with site restrictions
        """
        if domains is None:
            domains = COURT_DOMAINS

        # Build site restriction: (site:stj.jus.br OR site:tjsp.jus.br OR ...)
        site_clause = " OR ".join(f"site:{d}" for d in domains)
        return f"{query} ({site_clause})"

    async def search(
        self,
        query: str,
        max_results: int = 10,
        domains: list[str] = None,
    ) -> list[SearchResult]:
        """
        Search Google restricted to Brazilian court domains.

        Args:
            query: Search query (e.g., "dano moral contratual")
            max_results: Maximum results to return
            domains: Specific domains to search (defaults to all courts)

        Returns:
            List of SearchResult objects from court domains
        """
        logger.info(f"Google Courts search: '{query}' (max: {max_results})")

        # Build site-restricted query
        full_query = self._build_site_query(query, domains)
        logger.debug(f"Full query: {full_query}")

        params = {
            "q": full_query,
            "num": str(max_results + 5),  # Request extra for filtering
            "hl": "pt-BR",
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }

        try:
            url = f"{self.search_url}?{urllib.parse.urlencode(params)}"
            html = await self._fetch_page(url, headers=headers)
            return self._parse_results(html, max_results, domains or COURT_DOMAINS)

        except ScraperError as e:
            logger.error(f"Google Courts search failed: {e}")
            return []

    def _parse_results(
        self,
        html: str,
        max_results: int,
        allowed_domains: list[str],
    ) -> list[SearchResult]:
        """Parse Google search results, filtering to allowed domains."""
        soup = self._parse_html(html)
        results: list[SearchResult] = []

        # Google search results are in divs with class 'g'
        result_divs = soup.select("div.g")

        for div in result_divs:
            if len(results) >= max_results:
                break

            try:
                result = self._parse_single_result(div, allowed_domains)
                if result:
                    results.append(result)
            except Exception as e:
                logger.debug(f"Failed to parse result: {e}")
                continue

        logger.info(f"Parsed {len(results)} results from Google")
        return results

    def _parse_single_result(
        self,
        div,
        allowed_domains: list[str],
    ) -> Optional[SearchResult]:
        """Parse a single Google search result."""
        # Extract URL
        link = div.select_one("a[href]")
        if not link:
            return None

        url = link.get("href", "")
        if not url or not url.startswith("http"):
            return None

        # Check if URL is from allowed domain
        domain_match = None
        for domain in allowed_domains:
            if domain in url:
                domain_match = domain
                break

        if not domain_match:
            return None

        # Extract title
        title_el = div.select_one("h3")
        title = self._clean_text(title_el.get_text()) if title_el else ""

        if not title:
            return None

        # Extract snippet
        snippet_el = div.select_one("div[data-sncf], div.VwiC3b, span.aCOpRe")
        snippet = self._clean_text(snippet_el.get_text()) if snippet_el else ""

        # Determine tribunal from domain
        tribunal = self._domain_to_tribunal(domain_match)

        # Try to extract process number from title/snippet
        numero = None
        text = f"{title} {snippet}"
        numero_patterns = [
            r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",  # CNJ format
            r"(REsp|AgInt|AgRg|HC|RHC|MS|RMS|EREsp)\s*[\d\./-]+",
            r"(AC|AP|AI|Ag|RE|ARE)\s*\d+",
        ]

        for pattern in numero_patterns:
            match = re.search(pattern, text)
            if match:
                numero = match.group()
                break

        # Try to extract date
        data = None
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        if date_match:
            data = date_match.group(1)

        return SearchResult(
            url=url,
            title=title[:500],
            snippet=snippet[:300] if snippet else title[:200],
            tribunal=tribunal,
            numero_processo=numero,
            data_julgamento=data,
        )

    def _domain_to_tribunal(self, domain: str) -> str:
        """Convert domain to tribunal name."""
        mapping = {
            "stj.jus.br": "STJ",
            "stf.jus.br": "STF",
            "tjsp.jus.br": "TJSP",
            "tjmg.jus.br": "TJMG",
            "tjrj.jus.br": "TJRJ",
            "tst.jus.br": "TST",
            "trf1.jus.br": "TRF1",
            "trf2.jus.br": "TRF2",
            "trf3.jus.br": "TRF3",
            "trf4.jus.br": "TRF4",
            "trf5.jus.br": "TRF5",
            "cjf.jus.br": "CJF",
        }

        for key, value in mapping.items():
            if key in domain:
                return value
        return "Unknown"

    async def get_full_text(self, url: str) -> Optional[str]:
        """
        Fetch full text from a court URL.

        Note: This may fail due to CAPTCHA/session requirements.
        """
        try:
            html = await self._fetch_page(url)
            soup = self._parse_html(html)

            # Try common selectors for full text
            selectors = [
                "#integra",
                ".integra",
                ".inteiroTeor",
                ".ementa",
                "#conteudo",
                ".conteudo",
                "article",
                "main",
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = self._clean_text(element.get_text())
                    if len(text) > 100:
                        return text

            # Fallback: get body text
            body = soup.select_one("body")
            if body:
                return self._clean_text(body.get_text())[:10000]

            return None

        except Exception as e:
            logger.warning(f"Could not fetch full text from {url}: {e}")
            return None


# =============================================================================
# STANDALONE TEST
# =============================================================================

async def _test_google_courts_scraper():
    """Test the Google Courts scraper."""
    import asyncio

    print("Testing Google Courts Scraper...")
    print("(Uses Google Search restricted to court domains)")

    async with GoogleCourtsScraper() as scraper:
        results = await scraper.search("dano moral contratual", max_results=5)

        print(f"\nFound {len(results)} results:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. [{r.tribunal}] {r.numero_processo or 'N/A'}")
            print(f"   Title: {r.title[:80]}...")
            print(f"   URL: {r.url[:60]}...")
            if r.snippet:
                print(f"   Snippet: {r.snippet[:80]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_test_google_courts_scraper())
