"""
Tool de RAG (Retrieval-Augmented Generation) para agentes ADK.

Permite que agentes consultem a base de legislacao vetorizada
para fundamentar respostas com textos legais reais.

IMPORTANTE: A base e inicializada automaticamente na primeira consulta.
Se estiver vazia, baixa a CF e codigos principais automaticamente.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

from google.adk.tools import FunctionTool

from .vector_store import LegalVectorStore, SearchResult, load_and_index_corpus


# Singleton do vector store (inicializado sob demanda)
_vector_store: Optional[LegalVectorStore] = None
_initialization_lock = asyncio.Lock()
_initialized = False


async def _ensure_knowledge_base_ready() -> LegalVectorStore:
    """
    Garante que a base de conhecimento esta pronta.
    Se estiver vazia, baixa e indexa automaticamente.
    """
    global _vector_store, _initialized

    async with _initialization_lock:
        if _vector_store is None:
            home = Path.home()
            default_chroma = home / ".claude" / "legal-knowledge-base" / "chroma_db"
            chroma_dir = Path(os.environ.get("CHROMA_DIR", str(default_chroma)))
            _vector_store = LegalVectorStore(persist_dir=chroma_dir)

        # Verificar se base esta vazia
        stats = _vector_store.get_stats()
        doc_count = stats.get("document_count", 0)

        if doc_count == 0 and not _initialized:
            print("[RAG] Base de conhecimento vazia. Iniciando download automatico...")
            await _auto_initialize_knowledge_base()
            _initialized = True

    return _vector_store


async def _auto_initialize_knowledge_base() -> None:
    """Baixa e indexa corpus juridico automaticamente."""
    from .downloader import download_constituicao_abjur, download_codigos_principais

    home = Path.home()
    default_corpus = home / ".claude" / "legal-knowledge-base" / "corpus"
    corpus_dir = Path(os.environ.get("LEGAL_CORPUS_DIR", str(default_corpus)))
    corpus_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Baixar Constituicao Federal (rapido, ~300 artigos)
        print("[RAG] Baixando Constituicao Federal...")
        cf_docs = await download_constituicao_abjur(corpus_dir / "abjur")

        if cf_docs:
            print(f"[RAG] CF baixada: {len(cf_docs)} artigos")
            _vector_store.add_documents([d.to_dict() for d in cf_docs])

        # 2. Tentar baixar codigos principais do Planalto (pode demorar)
        print("[RAG] Baixando codigos principais do Planalto...")
        try:
            planalto_docs = await asyncio.wait_for(
                download_codigos_principais(corpus_dir / "planalto", delay=0.5),
                timeout=120  # 2 minutos max
            )
            if planalto_docs:
                print(f"[RAG] Planalto baixado: {len(planalto_docs)} codigos")
                _vector_store.add_documents([d.to_dict() for d in planalto_docs])
        except asyncio.TimeoutError:
            print("[RAG] Timeout no Planalto - continuando com CF apenas")
        except Exception as e:
            print(f"[RAG] Erro no Planalto: {e} - continuando com CF apenas")

        stats = _vector_store.get_stats()
        print(f"[RAG] Base inicializada: {stats.get('document_count', 0)} documentos")

    except Exception as e:
        print(f"[RAG] Erro na inicializacao: {e}")
        raise


def _get_vector_store() -> LegalVectorStore:
    """Obtem instancia singleton do vector store (sync, para compatibilidade)."""
    global _vector_store

    if _vector_store is None:
        home = Path.home()
        default_chroma = home / ".claude" / "legal-knowledge-base" / "chroma_db"
        chroma_dir = os.environ.get("CHROMA_DIR", str(default_chroma))
        _vector_store = LegalVectorStore(persist_dir=Path(chroma_dir))

    return _vector_store


async def search_legislation(
    query: str,
    n_results: int = 5,
    tipo: Optional[str] = None,
    include_full_text: bool = False
) -> Dict[str, Any]:
    """
    Busca semantica na base de legislacao brasileira.

    Use esta ferramenta para encontrar artigos de leis, codigos e normas
    relevantes para fundamentar seus argumentos juridicos.

    NOTA: Na primeira chamada, a base e inicializada automaticamente
    (baixa CF e codigos principais). Isso pode levar alguns segundos.

    Args:
        query: Consulta em linguagem natural (ex: "direito a moradia",
               "prazo prescricional danos morais", "legitima defesa")
        n_results: Numero de resultados a retornar (1-10, default: 5)
        tipo: Filtrar por tipo de documento:
              - "constituicao": Constituicao Federal
              - "codigo_civil": Codigo Civil
              - "codigo_penal": Codigo Penal
              - "cpc": Codigo de Processo Civil
              - "cpp": Codigo de Processo Penal
              - "clt": CLT
              - "cdc": Codigo de Defesa do Consumidor
              - "lei": Leis ordinarias
              - "decreto": Decretos
        include_full_text: Se True, inclui texto completo (pode ser longo)

    Returns:
        dict com:
            - status: "success" ou "error"
            - query: consulta realizada
            - result_count: numero de resultados
            - results: lista de documentos encontrados, cada um com:
                - titulo: titulo do documento
                - tipo: tipo de norma
                - fonte: origem do texto
                - relevancia: score de similaridade (0-1)
                - texto: trecho ou texto completo
                - citacao_sugerida: formato de citacao

    Exemplo de uso:
        # Buscar sobre prescricao
        resultado = await search_legislation(
            query="prazo prescricional acoes indenizatorias",
            tipo="codigo_civil",
            n_results=3
        )

        # Buscar na Constituicao
        resultado = await search_legislation(
            query="direitos fundamentais dignidade pessoa humana",
            tipo="constituicao"
        )
    """
    try:
        # Inicializa automaticamente se necessario
        store = await _ensure_knowledge_base_ready()

        # Limitar n_results
        n_results = max(1, min(10, n_results))

        # Executar busca
        results = store.search(
            query=query,
            n_results=n_results,
            tipo_filter=tipo
        )

        if not results:
            return {
                "status": "success",
                "query": query,
                "result_count": 0,
                "results": [],
                "message": "Nenhum documento encontrado. Tente reformular a consulta."
            }

        # Formatar resultados
        formatted_results = []

        for r in results:
            # Truncar texto se nao pediu completo
            texto = r.texto
            if not include_full_text and len(texto) > 1000:
                texto = texto[:1000] + "..."

            # Gerar sugestao de citacao
            citacao = _format_citation(r)

            formatted_results.append({
                "titulo": r.titulo,
                "tipo": r.tipo,
                "fonte": r.fonte,
                "relevancia": round(r.score, 3),
                "texto": texto,
                "citacao_sugerida": citacao
            })

        return {
            "status": "success",
            "query": query,
            "tipo_filtro": tipo,
            "result_count": len(formatted_results),
            "results": formatted_results
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Erro ao buscar na base de legislacao. Verifique se a base foi indexada."
        }


def _format_citation(result: SearchResult) -> str:
    """Formata citacao sugerida para o resultado."""
    tipo = result.tipo
    titulo = result.titulo

    if tipo == "constituicao":
        # Tentar extrair artigo
        if "Art." in titulo:
            return f"CF/88, {titulo}"
        return f"Constituicao Federal de 1988"

    elif tipo == "codigo_civil":
        return f"Codigo Civil (Lei 10.406/2002)"

    elif tipo == "codigo_penal":
        return f"Codigo Penal (Decreto-Lei 2.848/1940)"

    elif tipo == "cpc":
        return f"Codigo de Processo Civil (Lei 13.105/2015)"

    elif tipo == "cpp":
        return f"Codigo de Processo Penal (Decreto-Lei 3.689/1941)"

    elif tipo == "clt":
        return f"CLT (Decreto-Lei 5.452/1943)"

    elif tipo == "cdc":
        return f"Codigo de Defesa do Consumidor (Lei 8.078/1990)"

    elif tipo == "lei":
        return f"Legislacao Federal - {titulo}"

    elif tipo == "decreto":
        return f"Decreto Federal - {titulo}"

    else:
        return titulo or "Legislacao brasileira"


async def get_legislation_stats() -> Dict[str, Any]:
    """
    Retorna estatisticas da base de legislacao.

    Use para verificar se a base esta disponivel e quantos documentos contem.
    Se a base estiver vazia, inicia download automatico.

    Returns:
        dict com:
            - status: "success" ou "error"
            - document_count: numero total de documentos indexados
            - collection_name: nome da colecao
            - available: True se base esta operacional
    """
    try:
        store = await _ensure_knowledge_base_ready()
        stats = store.get_stats()

        return {
            "status": "success",
            "document_count": stats.get("document_count", 0),
            "collection_name": stats.get("collection_name", ""),
            "embedding_model": stats.get("embedding_model", ""),
            "available": stats.get("document_count", 0) > 0
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "available": False
        }


async def search_article(
    codigo: str,
    artigo: str
) -> Dict[str, Any]:
    """
    Busca um artigo especifico de um codigo.

    Args:
        codigo: Nome do codigo (constituicao, codigo_civil, codigo_penal,
                cpc, cpp, clt, cdc)
        artigo: Numero do artigo (ex: "5", "121", "927")

    Returns:
        dict com texto do artigo se encontrado

    Exemplo:
        # Buscar Art. 5 da CF
        resultado = await search_article(codigo="constituicao", artigo="5")

        # Buscar Art. 927 do CC
        resultado = await search_article(codigo="codigo_civil", artigo="927")
    """
    try:
        # Construir query especifica
        query = f"artigo {artigo} art. {artigo}"

        store = await _ensure_knowledge_base_ready()

        # Mapear nome para tipo
        tipo_map = {
            "constituicao": "constituicao",
            "cf": "constituicao",
            "codigo_civil": "codigo_civil",
            "cc": "codigo_civil",
            "codigo_penal": "codigo_penal",
            "cp": "codigo_penal",
            "cpc": "cpc",
            "cpp": "cpp",
            "clt": "clt",
            "cdc": "cdc",
        }

        tipo = tipo_map.get(codigo.lower(), codigo.lower())

        results = store.search(
            query=query,
            n_results=3,
            tipo_filter=tipo
        )

        # Filtrar por artigo exato
        for r in results:
            if f"Art. {artigo}" in r.titulo or f"art. {artigo}" in r.texto[:100].lower():
                return {
                    "status": "success",
                    "codigo": codigo,
                    "artigo": artigo,
                    "encontrado": True,
                    "titulo": r.titulo,
                    "texto": r.texto,
                    "citacao": _format_citation(r)
                }

        return {
            "status": "success",
            "codigo": codigo,
            "artigo": artigo,
            "encontrado": False,
            "message": f"Art. {artigo} do {codigo} nao encontrado na base. Tente usar search_legislation com uma descricao do conteudo."
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Registrar como FunctionTools
search_legislation_tool = FunctionTool(func=search_legislation)
get_legislation_stats_tool = FunctionTool(func=get_legislation_stats)
search_article_tool = FunctionTool(func=search_article)

# Export lista de tools
legal_rag_tools = [
    search_legislation_tool,
    get_legislation_stats_tool,
    search_article_tool
]
