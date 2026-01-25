"""
Tool para encerrar debates quando condicao de saida e atingida.
"""
from typing import List, Optional

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext


async def exit_debate(
    reason: str,
    verdict: str,
    confidence: str,
    remaining_issues: Optional[List[str]] = None,
    tool_context: ToolContext = None
) -> dict:
    """
    Encerra o debate atual, sinalizando que a condicao de saida foi atingida.

    USE ESTA FUNCAO APENAS QUANDO:
    - O output do agente construtivo esta APROVADO, ou
    - O numero maximo de iteracoes foi atingido e nao ha mais progresso, ou
    - Uma lacuna irresolvivel foi identificada que requer input do usuario

    Args:
        reason: Motivo do encerramento:
            - "approved": Output aprovado
            - "max_iterations": Limite de iteracoes atingido
            - "unresolvable": Lacuna irresolvivel
            - "user_input_needed": Requer input do usuario
            - "thesis_rejected": Tese nao sobrevive aos ataques
            - "citation_blocked": Citacao problematica bloqueia
        verdict: Resumo do veredicto final do debate
        confidence: Nivel de confianca no resultado (high | medium | low | blocked)
        remaining_issues: Lista de questoes nao resolvidas (se houver)

    Returns:
        dict confirmando encerramento
    """
    # Sinalizar escalation para o LoopAgent
    if tool_context:
        tool_context.actions.escalate = True

    return {
        "debate_ended": True,
        "reason": reason,
        "verdict": verdict,
        "confidence": confidence,
        "remaining_issues": remaining_issues or [],
        "action": "Controle retornado ao agente pai (SequentialAgent)"
    }


# Registrar como FunctionTool
exit_debate_tool = FunctionTool(func=exit_debate)
