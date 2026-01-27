"""
Downloader de corpus juridico brasileiro.

Fontes:
    1. LegalPT_dedup (HuggingFace) - 11.9M documentos
    2. Planalto.gov.br - Legislacao federal (scraping)
    3. abjur/constituicao - Constituicao Federal estruturada
"""

import os
import json
import re
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Diretorio base para dados
DATA_DIR = Path(os.environ.get("LEGAL_DATA_DIR", "./data/legal_corpus"))


@dataclass
class LegalDocument:
    """Documento juridico estruturado."""
    id: str
    tipo: str  # lei, decreto, constituicao, codigo, etc.
    titulo: str
    texto: str
    fonte: str  # planalto, huggingface, abjur
    url: Optional[str] = None
    data_publicacao: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LegalDocument":
        return cls(**data)


# ============================================================================
# HUGGINGFACE - LegalPT_dedup
# ============================================================================

def download_legalpt_dedup(
    subset: str = "ulysses-tesemo",
    max_samples: Optional[int] = None,
    output_dir: Optional[Path] = None
) -> Generator[LegalDocument, None, None]:
    """
    Baixa e processa o dataset LegalPT_dedup do HuggingFace.

    Args:
        subset: Nome do subset (ulysses-tesemo, acordaos-tcu, etc.)
        max_samples: Limite de documentos (None = todos)
        output_dir: Diretorio para cache

    Yields:
        LegalDocument para cada documento processado

    Subsets disponiveis:
        - all: Todos os dados
        - ulysses-tesemo: Documentos legislativos (1.74M)
        - acordaos-tcu: Acordaos do TCU (462K)
        - multilegal-pile-pt: MultiLegalPile portugues (6.26M)
        - brcad-5: Decisoes TRF5 (543K)
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Instale datasets: pip install datasets")

    output_dir = output_dir or DATA_DIR / "huggingface"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[HuggingFace] Baixando LegalPT_dedup subset={subset}...")

    # Carregar dataset (streaming para economia de memoria)
    dataset = load_dataset(
        "eduagarcia/LegalPT_dedup",
        name=subset,
        split="train",
        streaming=True
    )

    count = 0
    for item in dataset:
        if max_samples and count >= max_samples:
            break

        # Extrair campos relevantes
        text = item.get("text", "")
        source = item.get("source", subset)
        doc_id = item.get("id", f"{subset}_{count}")

        # Detectar tipo de documento pelo conteudo
        tipo = _detect_document_type(text)

        doc = LegalDocument(
            id=doc_id,
            tipo=tipo,
            titulo=_extract_title(text),
            texto=text,
            fonte="huggingface",
            metadata={
                "subset": subset,
                "original_source": source
            }
        )

        yield doc
        count += 1

        if count % 1000 == 0:
            print(f"[HuggingFace] Processados {count} documentos...")

    print(f"[HuggingFace] Total: {count} documentos do subset {subset}")


def _detect_document_type(text: str) -> str:
    """Detecta tipo de documento pelo conteudo."""
    text_lower = text[:500].lower()

    if "constituicao" in text_lower or "art. 5" in text_lower:
        return "constituicao"
    elif "codigo civil" in text_lower:
        return "codigo_civil"
    elif "codigo penal" in text_lower:
        return "codigo_penal"
    elif "codigo de processo" in text_lower:
        return "codigo_processual"
    elif "lei n" in text_lower or "lei complementar" in text_lower:
        return "lei"
    elif "decreto n" in text_lower or "decreto-lei" in text_lower:
        return "decreto"
    elif "medida provisoria" in text_lower:
        return "medida_provisoria"
    elif "sumula" in text_lower:
        return "sumula"
    elif "acordao" in text_lower or "ementa:" in text_lower:
        return "jurisprudencia"
    else:
        return "outro"


def _extract_title(text: str, max_len: int = 200) -> str:
    """Extrai titulo do documento."""
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 10:
            return line[:max_len]
    return text[:max_len]


# ============================================================================
# PLANALTO - Scraper de Legislacao Federal
# ============================================================================

PLANALTO_BASE = "https://www.planalto.gov.br"
PLANALTO_LEGISLACAO = f"{PLANALTO_BASE}/ccivil_03"

# URLs dos principais codigos e leis
CODIGOS_PRINCIPAIS = {
    "constituicao": f"{PLANALTO_LEGISLACAO}/constituicao/constituicao.htm",
    "codigo_civil": f"{PLANALTO_LEGISLACAO}/leis/2002/l10406compilada.htm",
    "codigo_penal": f"{PLANALTO_LEGISLACAO}/decreto-lei/del2848compilado.htm",
    "cpc": f"{PLANALTO_LEGISLACAO}/leis/l13105.htm",
    "cpp": f"{PLANALTO_LEGISLACAO}/decreto-lei/del3689compilado.htm",
    "clt": f"{PLANALTO_LEGISLACAO}/decreto-lei/del5452compilado.htm",
    "cdc": f"{PLANALTO_LEGISLACAO}/leis/l8078compilado.htm",
    "eca": f"{PLANALTO_LEGISLACAO}/leis/l8069.htm",
    "ctn": f"{PLANALTO_LEGISLACAO}/leis/l5172compilado.htm",
    "lei_execucao_penal": f"{PLANALTO_LEGISLACAO}/leis/l7210compilado.htm",
    "estatuto_idoso": f"{PLANALTO_LEGISLACAO}/leis/2003/l10.741.htm",
    "lgpd": f"{PLANALTO_LEGISLACAO}/leis/l13709.htm",
    "marco_civil_internet": f"{PLANALTO_LEGISLACAO}/leis/l12965.htm",
}


async def scrape_planalto_document(
    url: str,
    session: aiohttp.ClientSession,
    doc_type: str = "lei"
) -> Optional[LegalDocument]:
    """
    Faz scraping de um documento do Planalto.

    Args:
        url: URL do documento
        session: Sessao aiohttp
        doc_type: Tipo do documento

    Returns:
        LegalDocument ou None se falhar
    """
    try:
        async with session.get(url, timeout=30) as response:
            if response.status != 200:
                print(f"[Planalto] Erro {response.status}: {url}")
                return None

            html = await response.text()

            # Parse basico (sem BeautifulSoup para evitar dependencia)
            text = _extract_text_from_html(html)

            if not text or len(text) < 100:
                print(f"[Planalto] Documento vazio: {url}")
                return None

            # Extrair titulo
            title = _extract_title_from_html(html) or _extract_title(text)

            # Gerar ID unico
            doc_id = f"planalto_{doc_type}_{hash(url) % 10**8}"

            return LegalDocument(
                id=doc_id,
                tipo=doc_type,
                titulo=title,
                texto=text,
                fonte="planalto",
                url=url,
                metadata={"scraped_at": datetime.now().isoformat()}
            )

    except Exception as e:
        print(f"[Planalto] Erro ao baixar {url}: {e}")
        return None


def _extract_text_from_html(html: str) -> str:
    """Extrai texto limpo do HTML."""
    # Remover scripts e styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remover tags
    text = re.sub(r'<[^>]+>', ' ', html)

    # Limpar espacos
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # Decodificar entidades HTML comuns
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")

    return text


def _extract_title_from_html(html: str) -> Optional[str]:
    """Extrai titulo do HTML."""
    # Tentar <title>
    match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Tentar <h1>
    match = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None


async def download_codigos_principais(
    output_dir: Optional[Path] = None,
    delay: float = 1.0
) -> List[LegalDocument]:
    """
    Baixa os principais codigos do Planalto.

    Args:
        output_dir: Diretorio para salvar
        delay: Delay entre requests (respeitar servidor)

    Returns:
        Lista de documentos baixados
    """
    output_dir = output_dir or DATA_DIR / "planalto"
    output_dir.mkdir(parents=True, exist_ok=True)

    documents = []

    async with aiohttp.ClientSession() as session:
        for name, url in CODIGOS_PRINCIPAIS.items():
            print(f"[Planalto] Baixando {name}...")

            doc = await scrape_planalto_document(url, session, name)

            if doc:
                documents.append(doc)

                # Salvar individualmente
                doc_file = output_dir / f"{name}.json"
                with open(doc_file, "w", encoding="utf-8") as f:
                    json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)

                print(f"[Planalto] Salvo: {name} ({len(doc.texto)} chars)")

            # Rate limiting
            await asyncio.sleep(delay)

    print(f"[Planalto] Total: {len(documents)} documentos baixados")
    return documents


async def scrape_leis_ordinarias(
    ano_inicio: int = 2020,
    ano_fim: int = 2024,
    output_dir: Optional[Path] = None
) -> List[LegalDocument]:
    """
    Faz scraping de leis ordinarias por ano.

    Args:
        ano_inicio: Ano inicial
        ano_fim: Ano final
        output_dir: Diretorio para salvar

    Returns:
        Lista de documentos
    """
    output_dir = output_dir or DATA_DIR / "planalto" / "leis"
    output_dir.mkdir(parents=True, exist_ok=True)

    documents = []

    # URL base para listagem de leis por ano
    # Nota: O Planalto nao tem API, entao isso e aproximado
    base_patterns = [
        f"{PLANALTO_LEGISLACAO}/leis/{{ano}}/",
        f"{PLANALTO_LEGISLACAO}/leis/L{{ano}}.htm",
    ]

    async with aiohttp.ClientSession() as session:
        for ano in range(ano_inicio, ano_fim + 1):
            print(f"[Planalto] Buscando leis de {ano}...")

            # Tentar acessar pagina de indice do ano
            index_url = f"{PLANALTO_LEGISLACAO}/leis/{ano}/"

            try:
                async with session.get(index_url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Encontrar links para leis
                        lei_links = re.findall(
                            rf'href="([^"]*l{ano}\d+[^"]*\.htm)"',
                            html,
                            re.IGNORECASE
                        )

                        for link in lei_links[:50]:  # Limitar por ano
                            if not link.startswith("http"):
                                link = f"{PLANALTO_BASE}{link}"

                            doc = await scrape_planalto_document(link, session, "lei")
                            if doc:
                                documents.append(doc)

                            await asyncio.sleep(0.5)

            except Exception as e:
                print(f"[Planalto] Erro no ano {ano}: {e}")

    # Salvar todos
    all_file = output_dir / "leis_ordinarias.json"
    with open(all_file, "w", encoding="utf-8") as f:
        json.dump([d.to_dict() for d in documents], f, ensure_ascii=False, indent=2)

    print(f"[Planalto] Total leis ordinarias: {len(documents)}")
    return documents


# ============================================================================
# ABJUR - Constituicao Federal Estruturada
# ============================================================================

# URLs do ABJUR - Constituicao Federal (usar versao mais recente)
ABJUR_CF_API = "https://api.github.com/repos/abjur/constituicao/contents/JSON"
ABJUR_CF_LATEST = "https://raw.githubusercontent.com/abjur/constituicao/main/JSON/"


async def download_constituicao_abjur(
    output_dir: Optional[Path] = None,
    use_latest: bool = True
) -> List[LegalDocument]:
    """
    Baixa a Constituicao Federal estruturada do repo abjur.

    Args:
        output_dir: Diretorio para salvar
        use_latest: Se True, baixa apenas a versao mais recente

    Returns:
        Lista de documentos (um por artigo)
    """
    output_dir = output_dir or DATA_DIR / "abjur"
    output_dir.mkdir(parents=True, exist_ok=True)

    documents = []

    async with aiohttp.ClientSession() as session:
        print("[ABJUR] Buscando versoes da Constituicao Federal...")

        try:
            # Listar arquivos disponiveis
            async with session.get(ABJUR_CF_API, timeout=30) as response:
                if response.status != 200:
                    print(f"[ABJUR] Erro ao listar arquivos: {response.status}")
                    # Fallback: tentar URL direta da versao original
                    return await _download_cf_fallback(session, output_dir)

                files = await response.json()

                # Filtrar arquivos JSON e ordenar por data (mais recente primeiro)
                json_files = [f for f in files if f["name"].endswith(".json")]
                json_files.sort(key=lambda x: x["name"], reverse=True)

                if not json_files:
                    print("[ABJUR] Nenhum arquivo JSON encontrado")
                    return documents

                # Pegar o mais recente ou todos
                files_to_download = [json_files[0]] if use_latest else json_files

                for file_info in files_to_download:
                    file_name = file_info["name"]
                    download_url = file_info.get("download_url", f"{ABJUR_CF_LATEST}{file_name}")

                    print(f"[ABJUR] Baixando {file_name}...")

                    async with session.get(download_url, timeout=60) as file_response:
                        if file_response.status != 200:
                            print(f"[ABJUR] Erro ao baixar {file_name}: {file_response.status}")
                            continue

                        # Raw GitHub retorna text/plain, nao application/json
                        text = await file_response.text()
                        data = json.loads(text)

                        # Processar estrutura (lista de dispositivos)
                        version_docs = _parse_cf_json(data, file_name)
                        documents.extend(version_docs)

                        print(f"[ABJUR] {file_name}: {len(version_docs)} dispositivos")

        except Exception as e:
            print(f"[ABJUR] Erro: {e}")
            import traceback
            traceback.print_exc()

    # Salvar
    if documents:
        cf_file = output_dir / "constituicao_federal.json"
        with open(cf_file, "w", encoding="utf-8") as f:
            json.dump([d.to_dict() for d in documents], f, ensure_ascii=False, indent=2)

        print(f"[ABJUR] Total: {len(documents)} dispositivos da CF")

    return documents


def _parse_cf_json(data: Any, source_file: str) -> List[LegalDocument]:
    """
    Parse JSON hierarquico da CF do ABJUR.

    Estrutura:
    {
      "titulos": {
        "1": {
          "numero": ["I"],
          "texto": ["DOS PRINCIPIOS FUNDAMENTAIS"],
          "artigos": {
            "1": {
              "numero": ["1"],
              "texto": ["Art. 1..."],
              "incisos": {...},
              "paragrafos": {...}
            }
          }
        }
      }
    }
    """
    documents = []

    def extract_text(obj: Any) -> str:
        """Extrai texto de objeto (pode ser lista ou string)."""
        if isinstance(obj, list):
            return " ".join(str(x) for x in obj if x)
        elif isinstance(obj, str):
            return obj
        return ""

    def process_artigo(art_num: str, art_data: dict, titulo_nome: str = "") -> Optional[LegalDocument]:
        """Processa um artigo e seus dispositivos."""
        texto_parts = []

        # Texto principal do artigo (caput)
        caput = extract_text(art_data.get("texto", []))
        if caput:
            texto_parts.append(caput)

        # Incisos
        incisos = art_data.get("incisos", {})
        if isinstance(incisos, dict):
            for inc_num, inc_data in sorted(incisos.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                inc_texto = extract_text(inc_data.get("texto", []))
                if inc_texto:
                    texto_parts.append(inc_texto)

                # Alineas dentro do inciso
                alineas = inc_data.get("alineas", {})
                if isinstance(alineas, dict):
                    for al_num, al_data in sorted(alineas.items()):
                        al_texto = extract_text(al_data.get("texto", []))
                        if al_texto:
                            texto_parts.append(al_texto)

        # Paragrafos
        paragrafos = art_data.get("paragrafos", {})
        if isinstance(paragrafos, dict):
            for par_num, par_data in sorted(paragrafos.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                par_texto = extract_text(par_data.get("texto", []))
                if par_texto:
                    texto_parts.append(par_texto)

        texto_completo = "\n".join(texto_parts)

        if not texto_completo or len(texto_completo) < 10:
            return None

        return LegalDocument(
            id=f"cf_art_{art_num}",
            tipo="constituicao",
            titulo=f"CF - Art. {art_num}" + (f" ({titulo_nome})" if titulo_nome else ""),
            texto=texto_completo,
            fonte="abjur",
            url="https://github.com/abjur/constituicao",
            metadata={
                "artigo": art_num,
                "titulo": titulo_nome,
                "source_file": source_file
            }
        )

    # Navegar pela estrutura hierarquica
    if not isinstance(data, dict):
        return documents

    titulos = data.get("titulos", {})
    if not isinstance(titulos, dict):
        return documents

    for titulo_num, titulo_data in titulos.items():
        if not isinstance(titulo_data, dict):
            continue

        titulo_nome = extract_text(titulo_data.get("texto", []))

        # Artigos diretamente no titulo
        artigos = titulo_data.get("artigos", {})
        if isinstance(artigos, dict):
            for art_num, art_data in artigos.items():
                if isinstance(art_data, dict):
                    doc = process_artigo(art_num, art_data, titulo_nome)
                    if doc:
                        documents.append(doc)

        # Capitulos dentro do titulo
        capitulos = titulo_data.get("capitulos", {})
        if isinstance(capitulos, dict):
            for cap_num, cap_data in capitulos.items():
                if not isinstance(cap_data, dict):
                    continue

                cap_nome = extract_text(cap_data.get("texto", []))

                # Artigos no capitulo
                cap_artigos = cap_data.get("artigos", {})
                if isinstance(cap_artigos, dict):
                    for art_num, art_data in cap_artigos.items():
                        if isinstance(art_data, dict):
                            doc = process_artigo(art_num, art_data, f"{titulo_nome} - {cap_nome}")
                            if doc:
                                documents.append(doc)

                # Secoes dentro do capitulo
                secoes = cap_data.get("secoes", {})
                if isinstance(secoes, dict):
                    for sec_num, sec_data in secoes.items():
                        if not isinstance(sec_data, dict):
                            continue

                        sec_nome = extract_text(sec_data.get("texto", []))

                        sec_artigos = sec_data.get("artigos", {})
                        if isinstance(sec_artigos, dict):
                            for art_num, art_data in sec_artigos.items():
                                if isinstance(art_data, dict):
                                    doc = process_artigo(art_num, art_data, f"{titulo_nome} - {cap_nome} - {sec_nome}")
                                    if doc:
                                        documents.append(doc)

    return documents


async def _download_cf_fallback(
    session: aiohttp.ClientSession,
    output_dir: Path
) -> List[LegalDocument]:
    """Fallback: baixar CF do Planalto se ABJUR falhar."""
    print("[ABJUR] Usando fallback: Planalto...")

    doc = await scrape_planalto_document(
        CODIGOS_PRINCIPAIS["constituicao"],
        session,
        "constituicao"
    )

    if doc:
        cf_file = output_dir / "constituicao_federal.json"
        with open(cf_file, "w", encoding="utf-8") as f:
            json.dump([doc.to_dict()], f, ensure_ascii=False, indent=2)
        return [doc]

    return []


# ============================================================================
# CLI / MAIN
# ============================================================================

async def download_all(
    include_huggingface: bool = True,
    include_planalto: bool = True,
    include_abjur: bool = True,
    hf_max_samples: int = 10000,
    output_dir: Optional[Path] = None
) -> Dict[str, int]:
    """
    Baixa todos os corpus disponiveis.

    Args:
        include_huggingface: Baixar LegalPT_dedup
        include_planalto: Baixar Planalto (codigos principais)
        include_abjur: Baixar Constituicao do ABJUR
        hf_max_samples: Limite de amostras HuggingFace
        output_dir: Diretorio base

    Returns:
        Dict com contagem por fonte
    """
    output_dir = output_dir or DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = {}

    if include_abjur:
        docs = await download_constituicao_abjur(output_dir / "abjur")
        stats["abjur"] = len(docs)

    if include_planalto:
        docs = await download_codigos_principais(output_dir / "planalto")
        stats["planalto"] = len(docs)

    if include_huggingface:
        count = 0
        hf_dir = output_dir / "huggingface"
        hf_dir.mkdir(parents=True, exist_ok=True)

        # Salvar em batches
        batch = []
        batch_num = 0

        for doc in download_legalpt_dedup(
            subset="ulysses-tesemo",
            max_samples=hf_max_samples
        ):
            batch.append(doc.to_dict())
            count += 1

            if len(batch) >= 1000:
                batch_file = hf_dir / f"batch_{batch_num:04d}.json"
                with open(batch_file, "w", encoding="utf-8") as f:
                    json.dump(batch, f, ensure_ascii=False)
                batch = []
                batch_num += 1

        # Salvar ultimo batch
        if batch:
            batch_file = hf_dir / f"batch_{batch_num:04d}.json"
            with open(batch_file, "w", encoding="utf-8") as f:
                json.dump(batch, f, ensure_ascii=False)

        stats["huggingface"] = count

    print(f"\n[Download] Completo! Stats: {stats}")
    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download corpus juridico brasileiro")
    parser.add_argument("--no-hf", action="store_true", help="Pular HuggingFace")
    parser.add_argument("--no-planalto", action="store_true", help="Pular Planalto")
    parser.add_argument("--no-abjur", action="store_true", help="Pular ABJUR")
    parser.add_argument("--hf-limit", type=int, default=10000, help="Limite HuggingFace")
    parser.add_argument("--output", type=str, default="./data/legal_corpus", help="Diretorio de saida")

    args = parser.parse_args()

    asyncio.run(download_all(
        include_huggingface=not args.no_hf,
        include_planalto=not args.no_planalto,
        include_abjur=not args.no_abjur,
        hf_max_samples=args.hf_limit,
        output_dir=Path(args.output)
    ))
