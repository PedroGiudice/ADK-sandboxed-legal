"""
Base scraper interface for tribunal websites.

All tribunal scrapers must inherit from BaseScraper and implement
the abstract methods for searching and fetching full text.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging
import asyncio

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from bs4 import BeautifulSoup

# Handle both package and standalone imports
try:
    from ..models import SearchResult
except ImportError:
    from models import SearchResult


logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class RateLimitError(ScraperError):
    """Raised when rate limited by the tribunal website."""
    pass


class ParseError(ScraperError):
    """Raised when HTML parsing fails."""
    pass


class BaseScraper(ABC):
    """
    Abstract base class for tribunal scrapers.

    Provides common HTTP client setup, retry logic, and interface
    that all scrapers must implement.

    Attributes:
        client: Async HTTP client with retry logic
        user_agent: User-Agent string for requests
        timeout: Request timeout in seconds
        delay_between_requests: Delay between requests in seconds
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_DELAY = 1.0  # 1 second between requests

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        delay: float = DEFAULT_DELAY,
    ):
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self.timeout = timeout
        self.delay = delay
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time: float = 0

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not in context manager."""
        if self._client is None:
            raise RuntimeError(
                "Scraper must be used as async context manager: "
                "async with Scraper() as scraper:"
            )
        return self._client

    @property
    @abstractmethod
    def tribunal_name(self) -> str:
        """
        Name of the tribunal (e.g., 'STJ', 'TJSP').

        Used for identification in results.
        """
        pass

    @property
    @abstractmethod
    def tribunal_full_name(self) -> str:
        """
        Full name of the tribunal.

        E.g., 'Superior Tribunal de Justica'
        """
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """
        Base URL of the tribunal's jurisprudence portal.

        E.g., 'https://scon.stj.jus.br'
        """
        pass

    @property
    @abstractmethod
    def search_url(self) -> str:
        """
        URL for executing searches.

        May include query parameters template.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """
        Execute a search query and return parsed results.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of SearchResult objects

        Raises:
            ScraperError: If search fails
        """
        pass

    @abstractmethod
    async def get_full_text(self, url: str) -> Optional[str]:
        """
        Fetch the full text (inteiro teor) of a decision.

        Args:
            url: URL to the decision page

        Returns:
            Full text content or None if not available
        """
        pass

    async def _respect_rate_limit(self):
        """Wait between requests to avoid rate limiting."""
        import time

        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def _fetch_page(self, url: str, **kwargs) -> str:
        """
        Fetch a page with retry logic and rate limiting.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for httpx.get

        Returns:
            Page HTML content

        Raises:
            RateLimitError: If rate limited (429)
            ScraperError: If fetch fails after retries
        """
        await self._respect_rate_limit()

        try:
            response = await self.client.get(url, **kwargs)

            if response.status_code == 429:
                raise RateLimitError(f"Rate limited by {self.tribunal_name}")

            response.raise_for_status()
            return response.text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
            raise ScraperError(f"HTTP {e.response.status_code}: {e}") from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            raise ScraperError(str(e)) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def _post_page(
        self,
        url: str,
        data: Optional[dict] = None,
        **kwargs,
    ) -> str:
        """
        POST to a page with retry logic and rate limiting.

        Args:
            url: URL to POST to
            data: Form data to send
            **kwargs: Additional arguments for httpx.post

        Returns:
            Page HTML content
        """
        await self._respect_rate_limit()

        try:
            response = await self.client.post(url, data=data, **kwargs)

            if response.status_code == 429:
                raise RateLimitError(f"Rate limited by {self.tribunal_name}")

            response.raise_for_status()
            return response.text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error posting to {url}: {e.response.status_code}")
            raise ScraperError(f"HTTP {e.response.status_code}: {e}") from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error posting to {url}: {e}")
            raise ScraperError(str(e)) from e

    def _parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.

        Args:
            html: Raw HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "lxml")

    def _clean_text(self, text: Optional[str]) -> str:
        """
        Clean text content (remove extra whitespace, etc).

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""
        return " ".join(text.split())
