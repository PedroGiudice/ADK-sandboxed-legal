#!/usr/bin/env python3
"""
Unit tests for ADK agents.

Run with: pytest adk-agents/ -v
"""

import pytest
import json
from pathlib import Path

# Import agents
try:
    from iterative_research_agent import (
        IterativeResearchAgent,
        IterativeResearchConfig,
        Source,
        IterationResult,
        ResearchResult
    )
    ITERATIVE_AVAILABLE = True
except ImportError:
    ITERATIVE_AVAILABLE = False

try:
    from jurisprudence_agent.agent import (
        JurisprudenceAgent,
        JurisprudenceConfig,
        JurisprudenceSource,
        COURT_DOMAINS,
        DEFAULT_DOMAINS
    )
    JURISPRUDENCE_AVAILABLE = True
except ImportError:
    JURISPRUDENCE_AVAILABLE = False


# =============================================================================
# ITERATIVE RESEARCH AGENT TESTS
# =============================================================================

@pytest.mark.skipif(not ITERATIVE_AVAILABLE, reason="iterative_research_agent not available")
class TestIterativeResearchConfig:
    """Tests for IterativeResearchConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = IterativeResearchConfig()
        assert config.max_iterations == 5
        assert config.min_sources == 20
        assert config.saturation_threshold == 0.8
        assert config.model_name == "gemini-2.5-flash"

    def test_custom_config(self, temp_output_dir):
        """Test custom configuration."""
        config = IterativeResearchConfig(
            max_iterations=3,
            min_sources=10,
            output_dir=temp_output_dir
        )
        assert config.max_iterations == 3
        assert config.min_sources == 10
        assert config.output_dir == temp_output_dir

    def test_output_dir_created(self, tmp_path):
        """Test that output directory is created on init."""
        output_dir = tmp_path / "new_output"
        config = IterativeResearchConfig(output_dir=output_dir)
        assert output_dir.exists()


@pytest.mark.skipif(not ITERATIVE_AVAILABLE, reason="iterative_research_agent not available")
class TestSource:
    """Tests for Source dataclass."""

    def test_source_creation(self):
        """Test basic source creation."""
        source = Source(
            url="https://example.com",
            title="Test",
            snippet="Snippet"
        )
        assert source.url == "https://example.com"
        assert source.title == "Test"
        assert source.iteration == 0

    def test_source_equality(self):
        """Test source equality based on URL."""
        s1 = Source(url="https://example.com", title="Title 1")
        s2 = Source(url="https://example.com", title="Title 2")
        s3 = Source(url="https://other.com", title="Title 1")

        assert s1 == s2  # Same URL
        assert s1 != s3  # Different URL

    def test_source_hash(self):
        """Test source hashing for set usage."""
        s1 = Source(url="https://example.com", title="Title 1")
        s2 = Source(url="https://example.com", title="Title 2")

        source_set = {s1, s2}
        assert len(source_set) == 1  # Deduplicated by URL


@pytest.mark.skipif(not ITERATIVE_AVAILABLE, reason="iterative_research_agent not available")
class TestIterativeResearchAgent:
    """Tests for IterativeResearchAgent."""

    def test_agent_initialization(self, temp_output_dir):
        """Test agent initialization."""
        config = IterativeResearchConfig(output_dir=temp_output_dir)
        agent = IterativeResearchAgent(config)

        assert agent.config == config
        assert agent._agent is None  # Lazy init
        assert len(agent._collected_sources) == 0

    def test_stopping_criteria_min_sources(self, temp_output_dir):
        """Test stopping when min_sources reached."""
        config = IterativeResearchConfig(
            min_sources=5,
            output_dir=temp_output_dir
        )
        agent = IterativeResearchAgent(config)

        # Simulate collected sources
        for i in range(5):
            agent._collected_sources.add(Source(
                url=f"https://example.com/{i}",
                title=f"Source {i}"
            ))

        iter_result = IterationResult(
            iteration=1,
            queries_executed=["test"],
            sources_found=[],
            gaps_identified=[],
            saturation_score=0.5
        )

        reason = agent._check_stopping_criteria(iter_result)
        assert reason is not None
        assert "min_sources_reached" in reason


# =============================================================================
# JURISPRUDENCE AGENT TESTS
# =============================================================================

@pytest.mark.skipif(not JURISPRUDENCE_AVAILABLE, reason="jurisprudence_agent not available")
class TestJurisprudenceConfig:
    """Tests for JurisprudenceConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = JurisprudenceConfig()
        assert config.max_iterations == 5
        assert config.min_sources == 15
        assert len(config.court_domains) > 0

    def test_court_domains(self):
        """Test court domains list."""
        assert "stj.jus.br" in DEFAULT_DOMAINS
        assert "stf.jus.br" in DEFAULT_DOMAINS
        assert "tjsp.jus.br" in DEFAULT_DOMAINS


@pytest.mark.skipif(not JURISPRUDENCE_AVAILABLE, reason="jurisprudence_agent not available")
class TestJurisprudenceSource:
    """Tests for JurisprudenceSource dataclass."""

    def test_source_with_metadata(self):
        """Test source with legal metadata."""
        source = JurisprudenceSource(
            url="https://stj.jus.br/acordao/123",
            title="REsp 123456/SP",
            tribunal="STJ",
            numero_processo="123456-78.2020.8.26.0100"
        )
        assert source.tribunal == "STJ"
        assert source.numero_processo is not None


@pytest.mark.skipif(not JURISPRUDENCE_AVAILABLE, reason="jurisprudence_agent not available")
class TestJurisprudenceAgent:
    """Tests for JurisprudenceAgent."""

    def test_agent_initialization(self, temp_output_dir):
        """Test agent initialization."""
        config = JurisprudenceConfig(output_dir=temp_output_dir)
        agent = JurisprudenceAgent(config)

        assert agent.config == config
        assert len(agent.config.court_domains) > 0

    def test_site_restriction_building(self, temp_output_dir):
        """Test site restriction clause building."""
        config = JurisprudenceConfig(
            court_domains=["stj.jus.br", "stf.jus.br"],
            output_dir=temp_output_dir
        )
        agent = JurisprudenceAgent(config)

        restriction = agent._build_site_restriction()
        assert "site:stj.jus.br" in restriction
        assert "site:stf.jus.br" in restriction
        assert " OR " in restriction

    def test_add_site_restriction(self, temp_output_dir):
        """Test adding site restriction to query."""
        config = JurisprudenceConfig(
            court_domains=["stj.jus.br"],
            output_dir=temp_output_dir
        )
        agent = JurisprudenceAgent(config)

        query = "responsabilidade civil"
        restricted = agent._add_site_restriction(query)

        assert query in restricted
        assert "site:stj.jus.br" in restricted


# =============================================================================
# INTEGRATION TESTS (require API key)
# =============================================================================

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(not ITERATIVE_AVAILABLE, reason="iterative_research_agent not available")
class TestIterativeResearchIntegration:
    """Integration tests that require API access."""

    @pytest.mark.asyncio
    async def test_full_research_flow(self, api_key, temp_output_dir):
        """Test complete research flow with real API."""
        config = IterativeResearchConfig(
            max_iterations=1,
            min_sources=3,
            output_dir=temp_output_dir
        )
        agent = IterativeResearchAgent(config)

        result = await agent.research("Python async programming basics")

        assert result.topic == "Python async programming basics"
        assert result.metadata["total_iterations"] >= 1
        # Content may or may not be generated depending on API response


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
