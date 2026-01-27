"""
Tools para a pipeline juridica brasileira.

Exports:
    - search_planalto_tool: Busca legislacao no Planalto.gov.br
    - search_jurisprudence_tool: Busca jurisprudencia em portais de tribunais
    - validate_citation_tool: Valida formato de citacoes juridicas
    - exit_debate_tool: Encerra debates quando condicao de saida e atingida
    - filesystem_tools: Tools de acesso ao filesystem (read, write, list)
    - shell_tools: Tools de busca com grep, find e comandos basicos
"""

from .legal_search import search_planalto_tool, search_jurisprudence_tool
from .citation_validator import validate_citation_tool
from .exit_debate import exit_debate_tool
from .filesystem import (
    filesystem_tools,
    read_file_tool,
    write_file_tool,
    append_file_tool,
    list_directory_tool,
    file_exists_tool,
)
from .shell_tools import (
    shell_tools,
    grep_files_tool,
    find_files_tool,
    run_shell_command_tool,
    count_lines_tool,
)

__all__ = [
    "search_planalto_tool",
    "search_jurisprudence_tool",
    "validate_citation_tool",
    "exit_debate_tool",
    "filesystem_tools",
    "read_file_tool",
    "write_file_tool",
    "append_file_tool",
    "list_directory_tool",
    "file_exists_tool",
    "shell_tools",
    "grep_files_tool",
    "find_files_tool",
    "run_shell_command_tool",
    "count_lines_tool",
]
