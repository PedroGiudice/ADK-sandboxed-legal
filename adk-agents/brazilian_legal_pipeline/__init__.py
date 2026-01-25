"""
Brazilian Legal Pipeline - Suite Dialetica ADK

Pipeline de raciocinio juridico brasileiro com arquitetura dialetica.

Executa debates adversariais em 3 fases:
1. VERIFICACAO: VERIFICADOR vs CETICO
2. CONSTRUCAO: CONSTRUTOR vs DESTRUIDOR
3. REDACAO: REDATOR vs CRITICO

Usage:
    from brazilian_legal_pipeline import BrazilianLegalPipeline, PipelineConfig

    config = PipelineConfig(max_debate_iterations=3)
    pipeline = BrazilianLegalPipeline(config)

    consultation = {
        "consulta": {"texto": "...", "tipo_solicitado": "parecer"},
        "fatos": [...],
        "normas_identificadas": [...],
    }

    result = await pipeline.run(consultation)
    print(result.final_output)
"""

from .config import PipelineConfig, config
from .agent import BrazilianLegalPipeline, PipelineResult, DebateResult, get_pipeline
from .loop_controller import (
    LoopController,
    LoopState,
    LoopStatus,
    Checkpoint,
    get_controller,
    set_controller,
    pause_global,
    resume_global,
    stop_global,
)

__all__ = [
    "BrazilianLegalPipeline",
    "PipelineConfig",
    "PipelineResult",
    "DebateResult",
    "config",
    "get_pipeline",
    # Loop control
    "LoopController",
    "LoopState",
    "LoopStatus",
    "Checkpoint",
    "get_controller",
    "set_controller",
    "pause_global",
    "resume_global",
    "stop_global",
]

__version__ = "4.0.0"
