"""
Tools de filesystem para agentes ADK.
Permite ler, escrever e listar arquivos de forma segura.
"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.adk.tools import FunctionTool


# Diretorio base seguro (sandbox)
WORKSPACE_ROOT = Path(os.environ.get("ADK_WORKSPACE", "./workspace")).resolve()


def _validate_path(file_path: str) -> Path:
    """Valida que o path esta dentro do workspace."""
    path = (WORKSPACE_ROOT / file_path).resolve()
    if not str(path).startswith(str(WORKSPACE_ROOT)):
        raise ValueError(f"Path traversal detectado: {file_path}")
    return path


async def read_file(
    file_path: str,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Le o conteudo de um arquivo no workspace.

    Args:
        file_path: Caminho relativo ao workspace
        encoding: Encoding do arquivo (default: utf-8)

    Returns:
        dict com status, conteudo e metadados
    """
    try:
        path = _validate_path(file_path)

        if not path.exists():
            return {
                "status": "error",
                "error": f"Arquivo nao encontrado: {file_path}",
                "path": str(path)
            }

        if not path.is_file():
            return {
                "status": "error",
                "error": f"Nao e um arquivo: {file_path}",
                "path": str(path)
            }

        content = path.read_text(encoding=encoding)

        return {
            "status": "success",
            "content": content,
            "path": str(path),
            "size": len(content),
            "encoding": encoding
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "path": file_path
        }


async def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> Dict[str, Any]:
    """
    Escreve conteudo em um arquivo no workspace.

    Args:
        file_path: Caminho relativo ao workspace
        content: Conteudo a escrever
        encoding: Encoding do arquivo (default: utf-8)
        create_dirs: Criar diretorios pais se nao existirem

    Returns:
        dict com status e metadados
    """
    try:
        path = _validate_path(file_path)

        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding=encoding)

        return {
            "status": "success",
            "path": str(path),
            "size": len(content),
            "encoding": encoding
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "path": file_path
        }


async def append_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Adiciona conteudo ao final de um arquivo.

    Args:
        file_path: Caminho relativo ao workspace
        content: Conteudo a adicionar
        encoding: Encoding do arquivo

    Returns:
        dict com status
    """
    try:
        path = _validate_path(file_path)

        with open(path, "a", encoding=encoding) as f:
            f.write(content)

        return {
            "status": "success",
            "path": str(path),
            "appended_size": len(content)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "path": file_path
        }


async def list_directory(
    dir_path: str = ".",
    pattern: str = "*",
    recursive: bool = False
) -> Dict[str, Any]:
    """
    Lista arquivos em um diretorio do workspace.

    Args:
        dir_path: Caminho relativo ao workspace
        pattern: Glob pattern para filtrar (default: *)
        recursive: Se True, busca recursivamente

    Returns:
        dict com lista de arquivos
    """
    try:
        path = _validate_path(dir_path)

        if not path.exists():
            return {
                "status": "error",
                "error": f"Diretorio nao encontrado: {dir_path}"
            }

        if not path.is_dir():
            return {
                "status": "error",
                "error": f"Nao e um diretorio: {dir_path}"
            }

        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))

        entries = []
        for f in files[:100]:  # Limite de 100 entradas
            rel_path = f.relative_to(WORKSPACE_ROOT)
            entries.append({
                "path": str(rel_path),
                "name": f.name,
                "is_dir": f.is_dir(),
                "size": f.stat().st_size if f.is_file() else 0
            })

        return {
            "status": "success",
            "directory": str(path),
            "pattern": pattern,
            "count": len(entries),
            "entries": entries
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "path": dir_path
        }


async def file_exists(file_path: str) -> Dict[str, Any]:
    """
    Verifica se um arquivo existe.

    Args:
        file_path: Caminho relativo ao workspace

    Returns:
        dict com status de existencia
    """
    try:
        path = _validate_path(file_path)
        return {
            "exists": path.exists(),
            "is_file": path.is_file() if path.exists() else False,
            "is_dir": path.is_dir() if path.exists() else False,
            "path": str(path)
        }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e),
            "path": file_path
        }


# Registrar como FunctionTools
read_file_tool = FunctionTool(func=read_file)
write_file_tool = FunctionTool(func=write_file)
append_file_tool = FunctionTool(func=append_file)
list_directory_tool = FunctionTool(func=list_directory)
file_exists_tool = FunctionTool(func=file_exists)

# Export all tools
filesystem_tools = [
    read_file_tool,
    write_file_tool,
    append_file_tool,
    list_directory_tool,
    file_exists_tool
]
