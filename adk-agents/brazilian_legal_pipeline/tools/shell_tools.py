"""
Tools de shell para agentes ADK.
Permite executar comandos de busca (grep, find) de forma segura e sandboxed.
"""
import os
import asyncio
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional

from google.adk.tools import FunctionTool


# Diretorio base seguro (sandbox)
WORKSPACE_ROOT = Path(os.environ.get("ADK_WORKSPACE", "./workspace")).resolve()

# Comandos permitidos (whitelist)
ALLOWED_COMMANDS = {
    "grep",
    "find",
    "wc",
    "head",
    "tail",
    "cat",
    "ls",
    "file",
    "stat",
    "du",
    "sort",
    "uniq",
    "cut",
    "tr",
    "sed",  # somente para transformacoes, nao edicao in-place
    "awk",
}


def _validate_path(file_path: str) -> Path:
    """Valida que o path esta dentro do workspace."""
    path = (WORKSPACE_ROOT / file_path).resolve()
    if not str(path).startswith(str(WORKSPACE_ROOT)):
        raise ValueError(f"Path traversal detectado: {file_path}")
    return path


async def grep_files(
    pattern: str,
    path: str = ".",
    recursive: bool = True,
    ignore_case: bool = False,
    context_lines: int = 0,
    file_pattern: Optional[str] = None,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Busca um padrao em arquivos usando grep.

    Args:
        pattern: Padrao regex a buscar
        path: Caminho relativo ao workspace (default: raiz)
        recursive: Busca recursiva em subdiretorios
        ignore_case: Ignora maiusculas/minusculas
        context_lines: Linhas de contexto antes/depois do match
        file_pattern: Filtro de arquivos (ex: "*.txt", "*.md")
        max_results: Limite de resultados (default: 100)

    Returns:
        dict com matches encontrados
    """
    try:
        target_path = _validate_path(path)

        if not target_path.exists():
            return {
                "status": "error",
                "error": f"Caminho nao encontrado: {path}"
            }

        # Construir comando grep seguro
        cmd = ["grep"]

        if recursive:
            cmd.append("-r")
        if ignore_case:
            cmd.append("-i")
        if context_lines > 0:
            cmd.extend(["-C", str(min(context_lines, 10))])

        # Adicionar numero da linha
        cmd.append("-n")

        # Limitar output
        cmd.extend(["-m", str(max_results)])

        # Padrao e path
        cmd.append("--")  # Fim das opcoes
        cmd.append(pattern)

        if file_pattern:
            cmd.extend(["--include", file_pattern])

        cmd.append(str(target_path))

        # Executar
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(WORKSPACE_ROOT)
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        output = stdout.decode("utf-8", errors="replace")
        lines = output.strip().split("\n") if output.strip() else []

        # Processar resultados
        matches = []
        for line in lines[:max_results]:
            if ":" in line:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_path = parts[0]
                    line_num = parts[1]
                    content = parts[2]

                    # Converter path absoluto para relativo
                    try:
                        rel_path = str(Path(file_path).relative_to(WORKSPACE_ROOT))
                    except ValueError:
                        rel_path = file_path

                    matches.append({
                        "file": rel_path,
                        "line": int(line_num) if line_num.isdigit() else 0,
                        "content": content[:500]  # Limitar tamanho
                    })

        return {
            "status": "success",
            "pattern": pattern,
            "path": path,
            "match_count": len(matches),
            "matches": matches
        }

    except asyncio.TimeoutError:
        return {
            "status": "error",
            "error": "Timeout: busca demorou mais de 30 segundos"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def find_files(
    name_pattern: Optional[str] = None,
    path: str = ".",
    file_type: Optional[str] = None,
    extension: Optional[str] = None,
    max_results: int = 100,
    modified_within_days: Optional[int] = None
) -> Dict[str, Any]:
    """
    Encontra arquivos por nome, tipo ou extensao.

    Args:
        name_pattern: Padrao de nome (glob, ex: "*.pdf", "contrato*")
        path: Caminho relativo ao workspace
        file_type: Tipo: "f" (arquivo), "d" (diretorio)
        extension: Extensao sem ponto (ex: "pdf", "docx")
        max_results: Limite de resultados
        modified_within_days: Arquivos modificados nos ultimos N dias

    Returns:
        dict com arquivos encontrados
    """
    try:
        target_path = _validate_path(path)

        if not target_path.exists():
            return {
                "status": "error",
                "error": f"Caminho nao encontrado: {path}"
            }

        # Construir comando find
        cmd = ["find", str(target_path)]

        if file_type:
            cmd.extend(["-type", file_type])

        if name_pattern:
            cmd.extend(["-name", name_pattern])
        elif extension:
            cmd.extend(["-name", f"*.{extension}"])

        if modified_within_days:
            cmd.extend(["-mtime", f"-{modified_within_days}"])

        # Executar
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(WORKSPACE_ROOT)
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        output = stdout.decode("utf-8", errors="replace")
        lines = [l for l in output.strip().split("\n") if l]

        files = []
        for line in lines[:max_results]:
            abs_path = Path(line)
            try:
                rel_path = str(abs_path.relative_to(WORKSPACE_ROOT))
                stat = abs_path.stat() if abs_path.exists() else None
                files.append({
                    "path": rel_path,
                    "name": abs_path.name,
                    "is_dir": abs_path.is_dir(),
                    "size": stat.st_size if stat and abs_path.is_file() else 0
                })
            except (ValueError, OSError):
                continue

        return {
            "status": "success",
            "search_path": path,
            "file_count": len(files),
            "files": files
        }

    except asyncio.TimeoutError:
        return {
            "status": "error",
            "error": "Timeout: busca demorou mais de 30 segundos"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def run_shell_command(
    command: str,
    working_dir: str = "."
) -> Dict[str, Any]:
    """
    Executa um comando shell seguro (whitelist) no workspace.

    Args:
        command: Comando a executar (deve comecar com comando permitido)
        working_dir: Diretorio de trabalho relativo ao workspace

    Returns:
        dict com stdout, stderr e exit code

    Comandos permitidos: grep, find, wc, head, tail, cat, ls, file, stat, du, sort, uniq, cut, tr, sed, awk
    """
    try:
        # Parse command
        parts = shlex.split(command)
        if not parts:
            return {
                "status": "error",
                "error": "Comando vazio"
            }

        base_cmd = parts[0]

        # Verificar whitelist
        if base_cmd not in ALLOWED_COMMANDS:
            return {
                "status": "error",
                "error": f"Comando nao permitido: {base_cmd}. Permitidos: {', '.join(sorted(ALLOWED_COMMANDS))}"
            }

        # Verificar flags perigosas
        dangerous_flags = ["-i", "--in-place", "-exec", "-delete", "-ok"]
        for flag in dangerous_flags:
            if flag in parts:
                return {
                    "status": "error",
                    "error": f"Flag nao permitida: {flag}"
                }

        # Validar working_dir
        work_path = _validate_path(working_dir)
        if not work_path.exists():
            work_path = WORKSPACE_ROOT

        # Substituir paths relativos por absolutos dentro do workspace
        safe_parts = [base_cmd]
        for part in parts[1:]:
            if not part.startswith("-") and "/" not in part and not part.startswith("."):
                # Argumento simples, manter
                safe_parts.append(part)
            elif part.startswith("-"):
                # Flag, manter
                safe_parts.append(part)
            else:
                # Pode ser path, validar
                try:
                    validated = _validate_path(part)
                    safe_parts.append(str(validated))
                except ValueError:
                    # Path invalido, pode ser padrao regex
                    safe_parts.append(part)

        # Executar
        proc = await asyncio.create_subprocess_exec(
            *safe_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(work_path)
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")

        # Limitar tamanho do output
        max_output = 50000
        if len(stdout_text) > max_output:
            stdout_text = stdout_text[:max_output] + f"\n... (truncado, {len(stdout_text)} bytes total)"

        return {
            "status": "success" if proc.returncode == 0 else "error",
            "command": command,
            "exit_code": proc.returncode,
            "stdout": stdout_text,
            "stderr": stderr_text[:5000] if stderr_text else ""
        }

    except asyncio.TimeoutError:
        return {
            "status": "error",
            "error": "Timeout: comando demorou mais de 30 segundos"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def count_lines(
    file_path: str,
    pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    Conta linhas em um arquivo, opcionalmente filtrando por padrao.

    Args:
        file_path: Caminho relativo ao workspace
        pattern: Padrao regex opcional para filtrar linhas

    Returns:
        dict com contagens
    """
    try:
        path = _validate_path(file_path)

        if not path.exists():
            return {
                "status": "error",
                "error": f"Arquivo nao encontrado: {file_path}"
            }

        if pattern:
            # grep -c para contar matches
            proc = await asyncio.create_subprocess_exec(
                "grep", "-c", pattern, str(path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            matching_lines = int(stdout.decode().strip() or "0")
        else:
            matching_lines = None

        # wc -l para total
        proc = await asyncio.create_subprocess_exec(
            "wc", "-l", str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        total_lines = int(stdout.decode().split()[0])

        result = {
            "status": "success",
            "file": file_path,
            "total_lines": total_lines
        }

        if matching_lines is not None:
            result["matching_lines"] = matching_lines
            result["pattern"] = pattern

        return result

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Registrar como FunctionTools
grep_files_tool = FunctionTool(func=grep_files)
find_files_tool = FunctionTool(func=find_files)
run_shell_command_tool = FunctionTool(func=run_shell_command)
count_lines_tool = FunctionTool(func=count_lines)

# Export all tools
shell_tools = [
    grep_files_tool,
    find_files_tool,
    run_shell_command_tool,
    count_lines_tool
]
