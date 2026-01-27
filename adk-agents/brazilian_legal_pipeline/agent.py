#!/usr/bin/env python3
"""
================================================================================
BRAZILIAN LEGAL PIPELINE - SUITE DIALETICA ADK
================================================================================

Pipeline de raciocinio juridico brasileiro com arquitetura dialetica.

Executa debates adversariais em 3 fases:
1. VERIFICACAO: VERIFICADOR vs CETICO (validacao de fontes)
2. CONSTRUCAO: CONSTRUTOR vs DESTRUIDOR (construcao de tese)
3. REDACAO: REDATOR vs CRITICO (producao de texto)

Arquitetura: Loop programatico com prompts especializados por fase.
Cada debate executa ate convergencia ou max_iterations.

Author: Lex-Vector Team
Version: 4.0.0

Dependencies:
    pip install google-adk google-genai python-dotenv httpx

Environment Variables Required:
    GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY

================================================================================
"""

import asyncio
import json
import os
import sys
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field

# ADK imports
try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search
    from google.genai import types
except ImportError as e:
    print(f"[FATAL] Missing Google ADK dependencies: {e}")
    print("Install with: pip install google-adk google-genai")
    sys.exit(1)

try:
    import httpx
except ImportError:
    print("[WARN] httpx not installed. Some tools may not work.")
    httpx = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Local imports
from .config import PipelineConfig, config as default_config
from .prompts import (
    INTAKE_INSTRUCTION,
    VERIFICADOR_INSTRUCTION,
    CETICO_INSTRUCTION,
    CONSTRUTOR_INSTRUCTION,
    DESTRUIDOR_INSTRUCTION,
    REDATOR_INSTRUCTION,
    CRITICO_INSTRUCTION,
    SYNTHESIZER_INSTRUCTION,
)
from .tools import filesystem_tools, shell_tools
from .knowledge_base import legal_rag_tools
from .loop_controller import LoopController, LoopState, set_controller


# ============================================================================
# SECTION 1: LOGGING
# ============================================================================

def setup_logging(config: PipelineConfig) -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger("BrazilianLegalPipeline")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger


# ============================================================================
# SECTION 2: DATA STRUCTURES
# ============================================================================

@dataclass
class DebateResult:
    """Result of a single debate phase."""
    phase: str
    iterations: int
    converged: bool
    final_output: str
    agent_outputs: List[Dict[str, Any]]
    exit_reason: str


@dataclass
class PipelineResult:
    """Final pipeline result."""
    consultation: Dict[str, Any]
    intake_analysis: Dict[str, Any]
    verification_result: DebateResult
    construction_result: DebateResult
    drafting_result: DebateResult
    final_output: str
    metadata: Dict[str, Any]
    errors: List[str]


# ============================================================================
# SECTION 3: TOOL FUNCTIONS
# ============================================================================

async def search_planalto(
    norm_type: str,
    number: str,
    year: str,
    article: Optional[str] = None
) -> Dict[str, Any]:
    """
    Busca legislacao no portal Planalto.gov.br.

    Args:
        norm_type: Tipo da norma (lei, lei_complementar, decreto, constituicao)
        number: Numero da norma
        year: Ano da norma
        article: Artigo especifico a extrair (opcional)

    Returns:
        dict com status, texto e metadados da norma
    """
    if httpx is None:
        return {"status": "error", "error": "httpx not installed"}

    base = "https://www.planalto.gov.br/ccivil_03"

    url_map = {
        "constituicao": f"{base}/constituicao/constituicao.htm",
        "lei_complementar": f"{base}/leis/lcp/Lcp{number}.htm",
        "lei": f"{base}/leis/L{number}.htm",
        "decreto": f"{base}/decreto/D{number}.htm",
        "decreto_lei": f"{base}/decreto-lei/Del{number}.htm",
    }

    # Leis pos-2000 tem estrutura diferente
    if norm_type == "lei" and int(year) >= 2000:
        period_start = (int(year) // 4) * 4 + 1
        period_end = period_start + 3
        period = f"{period_start}-{period_end}"
        url = f"{base}/_ato{period}/{year}/lei/L{number}.htm"
    else:
        url = url_map.get(norm_type, f"{base}/leis/L{number}.htm")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                text = response.text
                extracted = text

                if article:
                    pattern = rf"Art\.\s*{article}[^0-9][\s\S]*?(?=Art\.\s*\d|$)"
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted = match.group(0)

                return {
                    "status": "found",
                    "source": "planalto.gov.br",
                    "url": url,
                    "text": extracted[:5000],
                    "full_identifier": f"{norm_type.replace('_', ' ').title()} {number}/{year}",
                    "confidence": "high"
                }
            else:
                return {
                    "status": "not_found",
                    "source": "planalto.gov.br",
                    "url": url,
                    "error": f"HTTP {response.status_code}",
                    "confidence": "none"
                }

    except Exception as e:
        return {
            "status": "error",
            "source": "planalto.gov.br",
            "error": str(e),
            "confidence": "none"
        }


def validate_citation(citation: str, citation_type: str) -> Dict[str, Any]:
    """
    Valida formato e completude de uma citacao juridica.

    Args:
        citation: Texto da citacao a validar
        citation_type: Tipo (legislation | jurisprudence | sumula | doctrine)

    Returns:
        dict com resultado da validacao
    """
    errors: List[str] = []
    warnings: List[str] = []

    if citation_type == "legislation":
        pattern = r"(Lei|Decreto|CF|CPC|CC|CLT|CDC|ECA|CTB|CTN).*?(\d+)[./](\d{4})"
        if not re.search(pattern, citation, re.IGNORECASE):
            errors.append("Formato de legislacao invalido")
        if "art" not in citation.lower() and len(citation) > 20:
            warnings.append("Citacao de lei sem especificacao de artigo")

    elif citation_type == "jurisprudence":
        tribunals = ["STF", "STJ", "TST", "TSE", "TRF", "TRT", "TJ"]
        has_tribunal = any(t in citation.upper() for t in tribunals)
        if not has_tribunal:
            errors.append("Tribunal nao identificado")

        date_pattern = r"\d{2}[./]\d{2}[./]\d{4}"
        if not re.search(date_pattern, citation):
            errors.append("Data de julgamento nao encontrada")

    elif citation_type == "sumula":
        pattern = r"[Ss][uU]mula\s+(Vinculante\s+)?(\d+)\s+(do|STF|STJ|TST)"
        if not re.search(pattern, citation, re.IGNORECASE):
            errors.append("Formato de sumula invalido")

    elif citation_type == "doctrine":
        if "," not in citation:
            warnings.append("Citacao doutrinaria pode estar incompleta")
        if not re.search(r"\d{4}", citation):
            warnings.append("Ano da publicacao nao encontrado")

    return {
        "valid": len(errors) == 0,
        "citation": citation,
        "type": citation_type,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================================
# SECTION 4: BRAZILIAN LEGAL PIPELINE
# ============================================================================

class BrazilianLegalPipeline:
    """
    Pipeline de raciocinio juridico brasileiro com arquitetura dialetica.

    Executa debates adversariais entre agentes construtivos e anti-agentes:
    - VERIFICACAO: VERIFICADOR vs CETICO
    - CONSTRUCAO: CONSTRUTOR vs DESTRUIDOR
    - REDACAO: REDATOR vs CRITICO
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.logger = setup_logging(self.config)

        # ADK components (lazy init)
        self._agent: Optional[Agent] = None
        self._session_service: Optional[InMemorySessionService] = None
        self._runner: Optional[Runner] = None
        self._session_id: str = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Pipeline state
        self._state: Dict[str, Any] = {}

        self.logger.info(f"BrazilianLegalPipeline initialized | Model: {self.config.model}")

    async def _initialize_agent(self, instruction: str, name: str) -> None:
        """Initialize or reconfigure the ADK agent with new instruction."""
        # Combina google_search com filesystem, shell e RAG tools
        all_tools = [google_search] + filesystem_tools + shell_tools + legal_rag_tools

        self._agent = Agent(
            name=name,
            model=self.config.model,
            description="Brazilian Legal Pipeline Agent",
            instruction=instruction,
            tools=all_tools,
        )

        if self._session_service is None:
            self._session_service = InMemorySessionService()
            await self._session_service.create_session(
                app_name="brazilian_legal_pipeline",
                user_id="pipeline",
                session_id=self._session_id
            )

        self._runner = Runner(
            agent=self._agent,
            app_name="brazilian_legal_pipeline",
            session_service=self._session_service
        )

    async def _execute_prompt(self, prompt: str) -> str:
        """Execute a prompt and return the text response."""
        content = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        final_response = ""

        async for event in self._runner.run_async(
            user_id="pipeline",
            session_id=self._session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text

        return final_response

    async def run(self, consultation: Dict[str, Any]) -> PipelineResult:
        """
        Execute the full legal reasoning pipeline.

        Args:
            consultation: Structured legal consultation

        Returns:
            PipelineResult with all outputs
        """
        self._state = {"consultation": consultation}

        # Inicializar loop controller para controle externo
        # Usa checkpoint_dir dinamico baseado no workspace do caso
        self._loop_controller = LoopController(
            max_iterations=5,  # 5 fases no pipeline
            checkpoint_dir=self.config.get_checkpoint_dir(),
            checkpoint_interval=1
        )
        set_controller(self._loop_controller)
        self._loop_controller.start()

        result = PipelineResult(
            consultation=consultation,
            intake_analysis={},
            verification_result=None,
            construction_result=None,
            drafting_result=None,
            final_output="",
            metadata={
                "start_time": datetime.now().isoformat(),
                "model": self.config.model,
                "max_debate_iterations": self.config.max_debate_iterations,
            },
            errors=[]
        )

        self.logger.info("="*60)
        self.logger.info("BRAZILIAN LEGAL PIPELINE - INICIANDO")
        self.logger.info("="*60)

        try:
            # FASE 0: INTAKE
            self._loop_controller.set_phase("intake")
            await self._loop_controller.wait_if_paused()
            if self._loop_controller.should_stop():
                raise InterruptedError("Pipeline interrompido pelo usuario")

            self.logger.info("FASE 0: INTAKE - Analisando consulta...")
            result.intake_analysis = await self._run_intake(consultation)
            self._state["intake_analysis"] = result.intake_analysis
            self._loop_controller.update_state({"intake_analysis": "completed"})
            await self._loop_controller.iterate()

            # FASE 1: DEBATE DE VERIFICACAO
            self._loop_controller.set_phase("verification")
            await self._loop_controller.wait_if_paused()
            if self._loop_controller.should_stop():
                raise InterruptedError("Pipeline interrompido pelo usuario")

            self.logger.info("FASE 1: DEBATE DE VERIFICACAO")
            result.verification_result = await self._run_debate(
                phase="verification",
                constructive_instruction=VERIFICADOR_INSTRUCTION,
                adversarial_instruction=CETICO_INSTRUCTION,
                constructive_name="verificador",
                adversarial_name="cetico",
                context_keys=["intake_analysis"],
                output_key="verified_sources"
            )
            self._state["verified_sources"] = result.verification_result.final_output
            self._loop_controller.update_state({"verification": "completed"})
            await self._loop_controller.iterate()

            # FASE 2: DEBATE DE CONSTRUCAO
            self._loop_controller.set_phase("construction")
            await self._loop_controller.wait_if_paused()
            if self._loop_controller.should_stop():
                raise InterruptedError("Pipeline interrompido pelo usuario")

            self.logger.info("FASE 2: DEBATE DE CONSTRUCAO")
            result.construction_result = await self._run_debate(
                phase="construction",
                constructive_instruction=CONSTRUTOR_INSTRUCTION,
                adversarial_instruction=DESTRUIDOR_INSTRUCTION,
                constructive_name="construtor",
                adversarial_name="destruidor",
                context_keys=["intake_analysis", "verified_sources"],
                output_key="legal_thesis"
            )
            self._state["legal_thesis"] = result.construction_result.final_output
            self._loop_controller.update_state({"construction": "completed"})
            await self._loop_controller.iterate()

            # FASE 3: DEBATE DE REDACAO
            self._loop_controller.set_phase("drafting")
            await self._loop_controller.wait_if_paused()
            if self._loop_controller.should_stop():
                raise InterruptedError("Pipeline interrompido pelo usuario")

            self.logger.info("FASE 3: DEBATE DE REDACAO")
            result.drafting_result = await self._run_debate(
                phase="drafting",
                constructive_instruction=REDATOR_INSTRUCTION,
                adversarial_instruction=CRITICO_INSTRUCTION,
                constructive_name="redator",
                adversarial_name="critico",
                context_keys=["intake_analysis", "verified_sources", "legal_thesis"],
                output_key="draft_document"
            )
            self._state["draft_document"] = result.drafting_result.final_output
            self._loop_controller.update_state({"drafting": "completed"})
            await self._loop_controller.iterate()

            # FASE 4: SINTESE FINAL
            self._loop_controller.set_phase("synthesis")
            await self._loop_controller.wait_if_paused()
            if self._loop_controller.should_stop():
                raise InterruptedError("Pipeline interrompido pelo usuario")

            self.logger.info("FASE 4: SINTESE FINAL")
            result.final_output = await self._run_synthesis()
            self._loop_controller.complete(success=True)

            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["total_debates"] = 3
            result.metadata["success"] = True

            self.logger.info("="*60)
            self.logger.info("PIPELINE COMPLETO")
            self.logger.info("="*60)

        except InterruptedError as e:
            # Interrupcao controlada pelo usuario
            result.errors.append(f"Interrompido: {e}")
            self.logger.warning(f"Pipeline interrompido: {e}")
            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["success"] = False
            result.metadata["interrupted"] = True

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            result.errors.append(error_msg)
            self.logger.error(f"Pipeline failed: {error_msg}", exc_info=True)
            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["success"] = False
            if hasattr(self, '_loop_controller'):
                self._loop_controller.set_error(error_msg)

        return result

    async def _run_intake(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Run INTAKE agent to analyze consultation."""
        await self._initialize_agent(INTAKE_INSTRUCTION, "intake_agent")

        prompt = f"""
Analise a seguinte consulta juridica estruturada:

```json
{json.dumps(consultation, ensure_ascii=False, indent=2)}
```

Produza a analise no formato JSON especificado nas instrucoes.
"""

        response = await self._execute_prompt(prompt)

        # Try to parse JSON from response
        try:
            # Extract JSON from markdown code block if present
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(response)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse intake JSON, using raw response")
            return {"raw_analysis": response}

    async def _run_debate(
        self,
        phase: str,
        constructive_instruction: str,
        adversarial_instruction: str,
        constructive_name: str,
        adversarial_name: str,
        context_keys: List[str],
        output_key: str
    ) -> DebateResult:
        """
        Run a dialectical debate between constructive and adversarial agents.

        Returns when:
        - Adversarial agent approves (converged=True)
        - Max iterations reached (converged=False)
        """
        result = DebateResult(
            phase=phase,
            iterations=0,
            converged=False,
            final_output="",
            agent_outputs=[],
            exit_reason=""
        )

        # Build context from state
        context = {k: self._state.get(k, {}) for k in context_keys}
        context_str = json.dumps(context, ensure_ascii=False, indent=2)

        constructive_output = ""

        for iteration in range(1, self.config.max_debate_iterations + 1):
            self.logger.info(f"  Iteracao {iteration}/{self.config.max_debate_iterations}")

            # CONSTRUCTIVE AGENT
            await self._initialize_agent(constructive_instruction, constructive_name)

            if iteration == 1:
                constructive_prompt = f"""
CONTEXTO:
{context_str}

Execute sua tarefa conforme as instrucoes.
"""
            else:
                constructive_prompt = f"""
CONTEXTO:
{context_str}

FEEDBACK DO AGENTE ADVERSARIAL (iteracao anterior):
{adversarial_output}

Revise seu output considerando o feedback acima.
"""

            constructive_output = await self._execute_prompt(constructive_prompt)
            result.agent_outputs.append({
                "agent": constructive_name,
                "iteration": iteration,
                "output": constructive_output[:2000]  # Truncate for storage
            })

            self.logger.info(f"    [{constructive_name.upper()}] Output gerado")

            # ADVERSARIAL AGENT
            await self._initialize_agent(adversarial_instruction, adversarial_name)

            adversarial_prompt = f"""
CONTEXTO:
{context_str}

OUTPUT DO AGENTE CONSTRUTIVO:
{constructive_output}

Analise criticamente e decida:
- SE aprovado: Indique "APROVADO" claramente no inicio
- SE requer revisao: Liste os problemas encontrados

Sua analise:
"""

            adversarial_output = await self._execute_prompt(adversarial_prompt)
            result.agent_outputs.append({
                "agent": adversarial_name,
                "iteration": iteration,
                "output": adversarial_output[:2000]
            })

            self.logger.info(f"    [{adversarial_name.upper()}] Analise completa")

            result.iterations = iteration

            # Check for approval
            approval_indicators = ["APROVADO", "approved", "aprovado"]
            if any(indicator in adversarial_output.upper() for indicator in approval_indicators):
                result.converged = True
                result.exit_reason = "approved"
                self.logger.info(f"  Debate convergiu na iteracao {iteration}")
                break

        if not result.converged:
            result.exit_reason = "max_iterations"
            self.logger.info(f"  Debate encerrou por max_iterations")

        result.final_output = constructive_output
        return result

    async def _run_synthesis(self) -> str:
        """Run final synthesis to combine all outputs."""
        await self._initialize_agent(SYNTHESIZER_INSTRUCTION, "synthesizer_agent")

        context = {
            "intake_analysis": self._state.get("intake_analysis", {}),
            "verified_sources": self._state.get("verified_sources", ""),
            "legal_thesis": self._state.get("legal_thesis", ""),
            "draft_document": self._state.get("draft_document", ""),
        }

        prompt = f"""
Sintetize todo o processo dialetico em um output final coeso.

DADOS DO PIPELINE:
{json.dumps(context, ensure_ascii=False, indent=2)}

Produza o output final conforme as instrucoes.
"""

        return await self._execute_prompt(prompt)

    async def save_results(self, result: PipelineResult, filename: Optional[str] = None) -> Path:
        """Save pipeline results to file."""
        output_dir = self.config.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"legal_pipeline_{timestamp}"

        output_path = output_dir / f"{filename}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Brazilian Legal Pipeline - Output\n\n")
            f.write(f"**Gerado em:** {result.metadata.get('start_time', 'N/A')}\n")
            f.write(f"**Modelo:** {result.metadata.get('model', 'N/A')}\n")
            f.write(f"**Status:** {'Sucesso' if result.metadata.get('success') else 'Erro'}\n\n")
            f.write("---\n\n")
            f.write("## Output Final\n\n")
            f.write(result.final_output)
            f.write("\n\n---\n\n")
            f.write("## Metadados dos Debates\n\n")

            if result.verification_result:
                f.write(f"### Verificacao\n")
                f.write(f"- Iteracoes: {result.verification_result.iterations}\n")
                f.write(f"- Convergiu: {result.verification_result.converged}\n")
                f.write(f"- Motivo saida: {result.verification_result.exit_reason}\n\n")

            if result.construction_result:
                f.write(f"### Construcao\n")
                f.write(f"- Iteracoes: {result.construction_result.iterations}\n")
                f.write(f"- Convergiu: {result.construction_result.converged}\n")
                f.write(f"- Motivo saida: {result.construction_result.exit_reason}\n\n")

            if result.drafting_result:
                f.write(f"### Redacao\n")
                f.write(f"- Iteracoes: {result.drafting_result.iterations}\n")
                f.write(f"- Convergiu: {result.drafting_result.converged}\n")
                f.write(f"- Motivo saida: {result.drafting_result.exit_reason}\n\n")

            if result.errors:
                f.write("## Erros\n\n")
                for e in result.errors:
                    f.write(f"- {e}\n")

        self.logger.info(f"Resultados salvos em: {output_path}")
        return output_path


# ============================================================================
# SECTION 5: MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Uso: python -m brazilian_legal_pipeline.agent \"Sua consulta\"")
        print("\nOu importe e use programaticamente:")
        print("  from brazilian_legal_pipeline import BrazilianLegalPipeline")
        print("  pipeline = BrazilianLegalPipeline()")
        print("  result = await pipeline.run(consultation)")
        sys.exit(1)

    # Verify API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("[ERRO] Chave API nao encontrada. Configure GOOGLE_API_KEY.")
        sys.exit(1)

    # Build simple consultation from CLI args
    query = " ".join(sys.argv[1:])

    consultation = {
        "consulta": {
            "texto": query,
            "tipo_solicitado": "parecer",
            "urgencia": "media"
        },
        "contexto": {
            "area_direito": "geral"
        },
        "fatos": [],
        "normas_identificadas": [],
        "jurisprudencia_identificada": [],
        "documentos_anexos": [],
        "restricoes": {}
    }

    print(f"\n{'='*60}")
    print("BRAZILIAN LEGAL PIPELINE")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")

    pipeline = BrazilianLegalPipeline()
    result = await pipeline.run(consultation)
    output_path = await pipeline.save_results(result)

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETO")
    print(f"{'='*60}")
    print(f"Output salvo em: {output_path}")
    print(f"{'='*60}\n")

    if result.final_output:
        print(result.final_output[:1000])
        if len(result.final_output) > 1000:
            print(f"\n... [{len(result.final_output) - 1000} mais caracteres]")


if __name__ == "__main__":
    asyncio.run(main())


# Export for imports
root_agent = None  # Placeholder for compatibility

def get_pipeline() -> BrazilianLegalPipeline:
    """Factory function to get pipeline instance."""
    return BrazilianLegalPipeline()
