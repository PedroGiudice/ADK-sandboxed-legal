"""
Knowledge Base para Pipeline Juridica.

Modulos:
    - downloader: Download de datasets (HuggingFace, Planalto)
    - embeddings: Modelo de embedding local
    - vector_store: ChromaDB para busca vetorial
    - rag_tool: Tool de RAG para agentes ADK
"""

from .vector_store import LegalVectorStore
from .rag_tool import search_legislation_tool, legal_rag_tools

__all__ = [
    "LegalVectorStore",
    "search_legislation_tool",
    "legal_rag_tools",
]
