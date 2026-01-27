"""
Vector Store para busca semantica em legislacao.

Usa ChromaDB com embedding local (sentence-transformers ou similar).
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Diretorio base para persistencia (fora do repo, persistente)
_HOME = Path.home()
CHROMA_DIR = Path(os.environ.get("CHROMA_DIR", str(_HOME / ".claude" / "legal-knowledge-base" / "chroma_db")))


@dataclass
class SearchResult:
    """Resultado de busca vetorial."""
    id: str
    texto: str
    tipo: str
    titulo: str
    fonte: str
    score: float
    metadata: Dict[str, Any]


class LegalVectorStore:
    """
    Vector store para legislacao brasileira.

    Usa ChromaDB para persistencia e busca vetorial,
    com modelo de embedding local para privacidade.
    """

    def __init__(
        self,
        collection_name: str = "legislacao_brasileira",
        persist_dir: Optional[Path] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Inicializa o vector store.

        Args:
            collection_name: Nome da colecao ChromaDB
            persist_dir: Diretorio para persistencia
            embedding_model: Modelo sentence-transformers a usar
        """
        self.collection_name = collection_name
        self.persist_dir = persist_dir or CHROMA_DIR
        self.embedding_model_name = embedding_model

        self._client = None
        self._collection = None
        self._embedding_fn = None

    def _ensure_initialized(self) -> None:
        """Inicializa ChromaDB e embedding se necessario."""
        if self._client is not None:
            return

        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("Instale chromadb: pip install chromadb")

        # Criar diretorio se nao existir
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Configurar cliente persistente
        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Configurar funcao de embedding
        self._embedding_fn = self._create_embedding_function()

        # Obter ou criar colecao
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_fn,
            metadata={"description": "Legislacao brasileira vetorizada"}
        )

        print(f"[VectorStore] Inicializado: {self._collection.count()} documentos")

    def _create_embedding_function(self):
        """Cria funcao de embedding."""
        try:
            from chromadb.utils import embedding_functions
        except ImportError:
            raise ImportError("Instale chromadb: pip install chromadb")

        # Tentar usar sentence-transformers (local, privado)
        try:
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )
        except Exception as e:
            print(f"[VectorStore] Aviso: sentence-transformers nao disponivel ({e})")
            print("[VectorStore] Usando embedding default do ChromaDB")
            return embedding_functions.DefaultEmbeddingFunction()

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Adiciona documentos ao vector store.

        Args:
            documents: Lista de dicts com campos: id, texto, tipo, titulo, fonte
            batch_size: Tamanho do batch para insercao

        Returns:
            Numero de documentos adicionados
        """
        self._ensure_initialized()

        added = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            ids = []
            texts = []
            metadatas = []

            for doc in batch:
                doc_id = doc.get("id", f"doc_{added + len(ids)}")

                # Verificar se ja existe
                existing = self._collection.get(ids=[doc_id])
                if existing and existing["ids"]:
                    continue

                texto = doc.get("texto", "")
                if not texto or len(texto) < 50:
                    continue

                # Truncar texto muito longo (limite do embedding)
                if len(texto) > 8000:
                    texto = texto[:8000]

                ids.append(doc_id)
                texts.append(texto)

                # Montar metadados filtrando valores None (ChromaDB nao aceita)
                meta = {
                    "tipo": doc.get("tipo") or "desconhecido",
                    "titulo": (doc.get("titulo") or "")[:500],
                    "fonte": doc.get("fonte") or "",
                    "url": doc.get("url") or "",
                }
                # Remover chaves com valores vazios ou None
                meta = {k: v for k, v in meta.items() if v}
                metadatas.append(meta)

            if ids:
                self._collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
                added += len(ids)

            if (i + batch_size) % 1000 == 0:
                print(f"[VectorStore] Adicionados {added} documentos...")

        print(f"[VectorStore] Total adicionados: {added}")
        return added

    def search(
        self,
        query: str,
        n_results: int = 5,
        tipo_filter: Optional[str] = None,
        fonte_filter: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Busca semantica por documentos similares.

        Args:
            query: Texto da consulta
            n_results: Numero de resultados
            tipo_filter: Filtrar por tipo (lei, decreto, constituicao, etc.)
            fonte_filter: Filtrar por fonte (planalto, huggingface, etc.)

        Returns:
            Lista de SearchResult ordenados por relevancia
        """
        self._ensure_initialized()

        # Construir filtro
        where_filter = None
        if tipo_filter or fonte_filter:
            conditions = []
            if tipo_filter:
                conditions.append({"tipo": tipo_filter})
            if fonte_filter:
                conditions.append({"fonte": fonte_filter})

            if len(conditions) == 1:
                where_filter = conditions[0]
            else:
                where_filter = {"$and": conditions}

        # Executar busca
        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # Processar resultados
        search_results = []

        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                texto = results["documents"][0][i] if results["documents"] else ""
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 1.0

                # Converter distancia em score (0-1, maior = melhor)
                score = max(0, 1 - distance)

                search_results.append(SearchResult(
                    id=doc_id,
                    texto=texto,
                    tipo=metadata.get("tipo", ""),
                    titulo=metadata.get("titulo", ""),
                    fonte=metadata.get("fonte", ""),
                    score=score,
                    metadata=metadata
                ))

        return search_results

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do vector store."""
        self._ensure_initialized()

        count = self._collection.count()

        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_dir": str(self.persist_dir),
            "embedding_model": self.embedding_model_name
        }

    def clear(self) -> None:
        """Remove todos os documentos da colecao."""
        self._ensure_initialized()
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_fn
        )
        print(f"[VectorStore] Colecao {self.collection_name} limpa")


def load_and_index_corpus(
    corpus_dir: Path,
    vector_store: Optional[LegalVectorStore] = None
) -> LegalVectorStore:
    """
    Carrega corpus de arquivos JSON e indexa no vector store.

    Args:
        corpus_dir: Diretorio com arquivos JSON
        vector_store: Vector store existente (ou cria novo)

    Returns:
        LegalVectorStore populado
    """
    if vector_store is None:
        vector_store = LegalVectorStore()

    corpus_dir = Path(corpus_dir)

    if not corpus_dir.exists():
        print(f"[Index] Diretorio nao encontrado: {corpus_dir}")
        return vector_store

    # Encontrar arquivos JSON
    json_files = list(corpus_dir.rglob("*.json"))
    print(f"[Index] Encontrados {len(json_files)} arquivos JSON")

    all_docs = []

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Pode ser lista ou dict unico
            if isinstance(data, list):
                all_docs.extend(data)
            elif isinstance(data, dict):
                all_docs.append(data)

        except Exception as e:
            print(f"[Index] Erro ao ler {json_file}: {e}")

    print(f"[Index] Total de documentos carregados: {len(all_docs)}")

    if all_docs:
        vector_store.add_documents(all_docs)

    return vector_store


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerenciar vector store de legislacao")
    parser.add_argument("command", choices=["index", "search", "stats", "clear"])
    parser.add_argument("--corpus-dir", type=str, default="./data/legal_corpus")
    parser.add_argument("--query", type=str, help="Query para busca")
    parser.add_argument("--tipo", type=str, help="Filtro por tipo")
    parser.add_argument("-n", type=int, default=5, help="Numero de resultados")

    args = parser.parse_args()

    store = LegalVectorStore()

    if args.command == "index":
        load_and_index_corpus(Path(args.corpus_dir), store)

    elif args.command == "search":
        if not args.query:
            print("Erro: --query obrigatorio para busca")
        else:
            results = store.search(args.query, n_results=args.n, tipo_filter=args.tipo)
            for i, r in enumerate(results):
                print(f"\n--- Resultado {i+1} (score: {r.score:.3f}) ---")
                print(f"Tipo: {r.tipo} | Fonte: {r.fonte}")
                print(f"Titulo: {r.titulo}")
                print(f"Texto: {r.texto[:300]}...")

    elif args.command == "stats":
        stats = store.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == "clear":
        store.clear()
