"""
Gerenciador de sessoes para casos juridicos.
Orquestra o ciclo de vida de sessoes isoladas por caso.
"""
import asyncio
import json
import os
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from .config import PipelineConfig
from .git_state import GitStateBackend


@dataclass
class SessionInfo:
    """Informacoes de uma sessao."""
    session_id: str
    case_id: str
    case_path: Path
    created_at: str
    status: str = "active"  # active, paused, completed, error
    last_checkpoint: Optional[str] = None
    git_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "case_id": self.case_id,
            "case_path": str(self.case_path),
            "created_at": self.created_at,
            "status": self.status,
            "last_checkpoint": self.last_checkpoint,
            "git_commit": self.git_commit
        }


@dataclass
class PipelineResultSummary:
    """Resumo do resultado do pipeline."""
    success: bool
    phases_completed: List[str]
    output_path: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SessionManager:
    """
    Gerenciador de sessoes para o Legal Pipeline.

    Responsabilidades:
    - Criar/resumir sessoes
    - Gerenciar isolamento de estado por caso
    - Orquestrar pipeline com contexto correto
    - Emitir eventos para o frontend
    """

    # Arquivo de metadados da sessao
    SESSION_FILE = ".adk_session.json"

    def __init__(self):
        """Inicializa o gerenciador."""
        self._active_sessions: Dict[str, SessionInfo] = {}
        self._pipelines: Dict[str, Any] = {}  # session_id -> BrazilianLegalPipeline

    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emite evento para o frontend via stdout."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        print(f"__ADK_EVENT__{json.dumps(event, ensure_ascii=False)}__ADK_EVENT__", flush=True)

    def _validate_case_path(self, case_path: Path) -> None:
        """
        Valida se o caminho do caso e seguro e acessivel.

        Raises:
            PermissionError: Se nao tiver permissao
            ValueError: Se caminho invalido
        """
        case_path = Path(case_path).resolve()

        # Verificar se o diretorio existe ou pode ser criado
        if case_path.exists():
            if not case_path.is_dir():
                raise ValueError(f"Caminho existe mas nao e diretorio: {case_path}")
            if not os.access(case_path, os.W_OK):
                raise PermissionError(f"Sem permissao de escrita: {case_path}")
        else:
            # Verificar se o pai existe e tem permissao
            parent = case_path.parent
            if not parent.exists():
                raise ValueError(f"Diretorio pai nao existe: {parent}")
            if not os.access(parent, os.W_OK):
                raise PermissionError(f"Sem permissao para criar diretorio em: {parent}")

    def _create_case_structure(self, case_path: Path) -> None:
        """
        Cria estrutura de diretorios para o caso.

        Estrutura:
        - .adk_state/     # Checkpoints do LoopController
        - .git/           # Versionamento (criado pelo GitStateBackend)
        - .context/       # Futuro RAG (gitignored)
        - docs/           # Documentos do caso
        - drafts/         # Minutas geradas
        """
        case_path = Path(case_path)
        case_path.mkdir(parents=True, exist_ok=True)

        # Criar subdiretorios
        (case_path / ".adk_state").mkdir(exist_ok=True)
        (case_path / ".context").mkdir(exist_ok=True)
        (case_path / "docs").mkdir(exist_ok=True)
        (case_path / "drafts").mkdir(exist_ok=True)

    def _load_session_file(self, case_path: Path) -> Optional[Dict[str, Any]]:
        """Carrega arquivo de sessao se existir."""
        session_file = case_path / self.SESSION_FILE
        if session_file.exists():
            try:
                with open(session_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def _save_session_file(self, session: SessionInfo) -> None:
        """Salva arquivo de sessao."""
        session_file = Path(session.case_path) / self.SESSION_FILE
        with open(session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

    async def create_session(
        self,
        case_path: str,
        case_id: str
    ) -> SessionInfo:
        """
        Cria nova sessao para um caso.

        Args:
            case_path: Caminho do diretorio do caso
            case_id: ID unico do caso

        Returns:
            SessionInfo com dados da sessao

        Raises:
            PermissionError: Se nao tiver permissao
            ValueError: Se caminho invalido
        """
        case_path = Path(case_path).resolve()

        # Validar
        self._validate_case_path(case_path)

        # Criar estrutura
        self._create_case_structure(case_path)

        # Inicializar Git
        git_backend = GitStateBackend(case_path)

        # Criar sessao
        session = SessionInfo(
            session_id=str(uuid.uuid4()),
            case_id=case_id,
            case_path=case_path,
            created_at=datetime.now().isoformat(),
            status="active"
        )

        # Salvar
        self._save_session_file(session)
        self._active_sessions[session.session_id] = session

        # Commit inicial se houve mudancas
        if git_backend.is_available:
            commit_hash = git_backend.commit(
                "Sessao iniciada",
                auto=True,
                phase="init"
            )
            if commit_hash:
                session.git_commit = commit_hash
                git_backend.emit_event("session_created", {
                    "session_id": session.session_id,
                    "case_id": case_id,
                    "case_path": str(case_path),
                    "git_commit": commit_hash
                })

        # Emitir evento
        self._emit_event("session_created", session.to_dict())

        return session

    async def resume_session(self, case_path: str) -> SessionInfo:
        """
        Resume sessao existente.

        Args:
            case_path: Caminho do diretorio do caso

        Returns:
            SessionInfo da sessao resumida

        Raises:
            FileNotFoundError: Se sessao nao existir
        """
        case_path = Path(case_path).resolve()

        # Carregar sessao existente
        session_data = self._load_session_file(case_path)
        if not session_data:
            raise FileNotFoundError(f"Sessao nao encontrada em: {case_path}")

        session = SessionInfo(
            session_id=session_data["session_id"],
            case_id=session_data["case_id"],
            case_path=Path(session_data["case_path"]),
            created_at=session_data["created_at"],
            status="active",  # Reativar
            last_checkpoint=session_data.get("last_checkpoint"),
            git_commit=session_data.get("git_commit")
        )

        # Registrar
        self._active_sessions[session.session_id] = session

        # Emitir evento
        self._emit_event("session_resumed", session.to_dict())

        return session

    async def run_pipeline(
        self,
        session_id: str,
        consultation: Dict[str, Any]
    ) -> PipelineResultSummary:
        """
        Executa pipeline em uma sessao.

        Args:
            session_id: ID da sessao
            consultation: Dados da consulta juridica

        Returns:
            PipelineResultSummary com resultado

        Raises:
            KeyError: Se sessao nao existir
        """
        if session_id not in self._active_sessions:
            raise KeyError(f"Sessao nao encontrada: {session_id}")

        session = self._active_sessions[session_id]
        start_time = datetime.now()

        # Criar config com paths do caso
        config = PipelineConfig(
            workspace_path=Path(session.case_path),
            case_id=session.case_id
        )

        # Garantir diretorios
        config.ensure_directories()

        # Emitir inicio
        self._emit_event("pipeline_started", {
            "session_id": session_id,
            "case_id": session.case_id
        })

        try:
            # Import aqui para evitar circular
            from .agent import BrazilianLegalPipeline

            # Criar e executar pipeline
            pipeline = BrazilianLegalPipeline(config)
            self._pipelines[session_id] = pipeline

            result = await pipeline.run(consultation)

            # Salvar resultados
            output_path = await pipeline.save_results(result)

            # Commit automatico
            git_backend = GitStateBackend(session.case_path)
            if git_backend.is_available:
                commit_hash = git_backend.commit(
                    f"Pipeline completo: {result.metadata.get('success', False)}",
                    auto=True,
                    phase="complete"
                )
                session.git_commit = commit_hash

            # Atualizar sessao
            session.status = "completed" if result.metadata.get("success") else "error"
            self._save_session_file(session)

            duration = (datetime.now() - start_time).total_seconds()

            summary = PipelineResultSummary(
                success=result.metadata.get("success", False),
                phases_completed=[
                    "intake",
                    "verification" if result.verification_result else None,
                    "construction" if result.construction_result else None,
                    "drafting" if result.drafting_result else None,
                    "synthesis" if result.final_output else None
                ],
                output_path=str(output_path) if output_path else None,
                duration_seconds=duration
            )
            summary.phases_completed = [p for p in summary.phases_completed if p]

            # Emitir evento
            self._emit_event("pipeline_completed", {
                "session_id": session_id,
                "result": summary.to_dict()
            })

            return summary

        except Exception as e:
            session.status = "error"
            self._save_session_file(session)

            duration = (datetime.now() - start_time).total_seconds()

            summary = PipelineResultSummary(
                success=False,
                phases_completed=[],
                error=str(e),
                duration_seconds=duration
            )

            self._emit_event("pipeline_error", {
                "session_id": session_id,
                "error": str(e)
            })

            return summary

        finally:
            # Cleanup
            if session_id in self._pipelines:
                del self._pipelines[session_id]

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Retorna sessao ativa."""
        return self._active_sessions.get(session_id)

    def list_sessions(self) -> List[SessionInfo]:
        """Lista todas as sessoes ativas."""
        return list(self._active_sessions.values())

    async def pause_pipeline(self, session_id: str) -> bool:
        """Pausa pipeline em execucao."""
        if session_id not in self._pipelines:
            return False

        pipeline = self._pipelines[session_id]
        if hasattr(pipeline, "_loop_controller"):
            pipeline._loop_controller.pause()
            return True
        return False

    async def resume_pipeline(self, session_id: str) -> bool:
        """Resume pipeline pausado."""
        if session_id not in self._pipelines:
            return False

        pipeline = self._pipelines[session_id]
        if hasattr(pipeline, "_loop_controller"):
            pipeline._loop_controller.resume()
            return True
        return False

    async def stop_pipeline(self, session_id: str) -> bool:
        """Para pipeline em execucao."""
        if session_id not in self._pipelines:
            return False

        pipeline = self._pipelines[session_id]
        if hasattr(pipeline, "_loop_controller"):
            pipeline._loop_controller.stop()
            return True
        return False


# Singleton global
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Retorna o SessionManager global."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
