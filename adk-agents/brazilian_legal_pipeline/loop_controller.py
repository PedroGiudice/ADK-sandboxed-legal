"""
Controlador de loop para agentes ADK.
Permite pause, resume, stop e checkpointing.
"""
import asyncio
import json
import signal
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
import threading


class LoopState(Enum):
    """Estados possiveis do loop."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Checkpoint:
    """Checkpoint de estado do loop."""
    iteration: int
    phase: str
    state_data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        return cls(**data)


@dataclass
class LoopStatus:
    """Status atual do loop."""
    state: LoopState
    current_iteration: int
    max_iterations: int
    current_phase: str
    progress_percent: float
    last_checkpoint: Optional[Checkpoint] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "current_phase": self.current_phase,
            "progress_percent": self.progress_percent,
            "last_checkpoint": self.last_checkpoint.to_dict() if self.last_checkpoint else None,
            "error_message": self.error_message
        }


class LoopController:
    """
    Controlador de loop para agentes ADK.

    Permite:
    - Pause/Resume/Stop do loop
    - Checkpointing automatico
    - Callbacks para eventos
    - Comunicacao com frontend via stdout JSON
    """

    def __init__(
        self,
        max_iterations: int = 10,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_interval: int = 1,
        on_progress: Optional[Callable[[LoopStatus], None]] = None,
        on_checkpoint: Optional[Callable[[Checkpoint], None]] = None,
    ):
        self.max_iterations = max_iterations
        self.checkpoint_dir = Path(checkpoint_dir or "./checkpoints")
        self.checkpoint_interval = checkpoint_interval
        self.on_progress = on_progress
        self.on_checkpoint = on_checkpoint

        # Estado interno
        self._state = LoopState.IDLE
        self._current_iteration = 0
        self._current_phase = "init"
        self._state_data: Dict[str, Any] = {}
        self._last_checkpoint: Optional[Checkpoint] = None
        self._error_message: Optional[str] = None

        # Controle de sinais
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Inicia nao-pausado
        self._stop_requested = False

        # Setup signal handlers
        self._setup_signals()

    def _setup_signals(self):
        """Configura handlers para sinais do sistema."""
        def handle_pause(signum, frame):
            self.pause()

        def handle_stop(signum, frame):
            self.stop()

        # SIGUSR1 = pause, SIGUSR2 = resume, SIGTERM = stop
        if sys.platform != "win32":
            signal.signal(signal.SIGUSR1, handle_pause)
            signal.signal(signal.SIGUSR2, lambda s, f: self.resume())
            signal.signal(signal.SIGTERM, handle_stop)

    @property
    def state(self) -> LoopState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == LoopState.RUNNING

    @property
    def is_paused(self) -> bool:
        return self._state == LoopState.PAUSED

    def get_status(self) -> LoopStatus:
        """Retorna status atual do loop."""
        progress = (self._current_iteration / self.max_iterations) * 100 if self.max_iterations > 0 else 0
        return LoopStatus(
            state=self._state,
            current_iteration=self._current_iteration,
            max_iterations=self.max_iterations,
            current_phase=self._current_phase,
            progress_percent=min(progress, 100),
            last_checkpoint=self._last_checkpoint,
            error_message=self._error_message
        )

    def pause(self):
        """Pausa o loop."""
        if self._state == LoopState.RUNNING:
            self._state = LoopState.PAUSED
            self._pause_event.clear()
            self._emit_status()
            self._save_checkpoint()

    def resume(self):
        """Resume o loop pausado."""
        if self._state == LoopState.PAUSED:
            self._state = LoopState.RUNNING
            self._pause_event.set()
            self._emit_status()

    def stop(self):
        """Para o loop."""
        self._stop_requested = True
        self._pause_event.set()  # Libera se estava pausado
        self._save_checkpoint()

    def update_state(self, data: Dict[str, Any]):
        """Atualiza dados de estado."""
        self._state_data.update(data)

    def set_phase(self, phase: str):
        """Define a fase atual."""
        self._current_phase = phase
        self._emit_status()

    async def wait_if_paused(self):
        """Aguarda se o loop estiver pausado."""
        await self._pause_event.wait()

    def should_stop(self) -> bool:
        """Verifica se deve parar."""
        return self._stop_requested

    def should_continue(self) -> bool:
        """Verifica se deve continuar o loop."""
        return (
            not self._stop_requested and
            self._current_iteration < self.max_iterations
        )

    async def iterate(self) -> int:
        """
        Avanca uma iteracao.

        Returns:
            Numero da iteracao atual
        """
        await self.wait_if_paused()

        if self.should_stop():
            self._state = LoopState.STOPPED
            return -1

        self._current_iteration += 1

        # Checkpoint periodico
        if self._current_iteration % self.checkpoint_interval == 0:
            self._save_checkpoint()

        self._emit_status()
        return self._current_iteration

    def start(self):
        """Inicia o loop."""
        self._state = LoopState.RUNNING
        self._stop_requested = False
        self._current_iteration = 0
        self._emit_status()

    def complete(self, success: bool = True):
        """Marca o loop como completo."""
        self._state = LoopState.COMPLETED if success else LoopState.ERROR
        self._save_checkpoint()
        self._emit_status()

    def set_error(self, message: str):
        """Define erro no loop."""
        self._error_message = message
        self._state = LoopState.ERROR
        self._emit_status()

    def _save_checkpoint(self):
        """Salva checkpoint atual."""
        checkpoint = Checkpoint(
            iteration=self._current_iteration,
            phase=self._current_phase,
            state_data=self._state_data.copy()
        )
        self._last_checkpoint = checkpoint

        # Salvar em arquivo
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{checkpoint.timestamp.replace(':', '-')}.json"

        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=False)

        # Callback
        if self.on_checkpoint:
            self.on_checkpoint(checkpoint)

    def load_checkpoint(self, checkpoint_file: Path) -> Optional[Checkpoint]:
        """Carrega checkpoint de arquivo."""
        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file) as f:
            data = json.load(f)

        checkpoint = Checkpoint.from_dict(data)
        self._current_iteration = checkpoint.iteration
        self._current_phase = checkpoint.phase
        self._state_data = checkpoint.state_data
        self._last_checkpoint = checkpoint

        return checkpoint

    def load_latest_checkpoint(self) -> Optional[Checkpoint]:
        """Carrega o checkpoint mais recente."""
        if not self.checkpoint_dir.exists():
            return None

        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"), reverse=True)
        if not checkpoints:
            return None

        return self.load_checkpoint(checkpoints[0])

    def _emit_status(self):
        """Emite status para stdout em formato JSON."""
        status = self.get_status()

        # Formato JSON para o frontend
        event = {
            "type": "loop_status",
            "data": status.to_dict(),
            "timestamp": datetime.now().isoformat()
        }

        # Linha JSON para parsing pelo frontend
        print(f"__ADK_EVENT__{json.dumps(event, ensure_ascii=False)}__ADK_EVENT__", flush=True)

        # Callback
        if self.on_progress:
            self.on_progress(status)


# Singleton global para controle externo
_global_controller: Optional[LoopController] = None


def get_controller() -> Optional[LoopController]:
    """Retorna o controlador global."""
    return _global_controller


def set_controller(controller: LoopController):
    """Define o controlador global."""
    global _global_controller
    _global_controller = controller


# Funcoes de controle externo (para uso via stdin ou signals)
def pause_global():
    """Pausa o loop global."""
    if _global_controller:
        _global_controller.pause()


def resume_global():
    """Resume o loop global."""
    if _global_controller:
        _global_controller.resume()


def stop_global():
    """Para o loop global."""
    if _global_controller:
        _global_controller.stop()
