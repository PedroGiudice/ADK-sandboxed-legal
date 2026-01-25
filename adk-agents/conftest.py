#!/usr/bin/env python3
"""
Pytest configuration and fixtures for ADK agents tests.
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture
def api_key():
    """Get API key from environment or skip test."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not key:
        pytest.skip("No API key configured (GOOGLE_API_KEY)")
    return key


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for tests."""
    output_dir = tmp_path / "research_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def mock_search_result():
    """Mock search result for unit tests."""
    return {
        "url": "https://example.com/test",
        "title": "Test Result",
        "snippet": "This is a test snippet for unit testing."
    }
