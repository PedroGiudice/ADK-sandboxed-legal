"""
Backend de estado Git para casos juridicos.
Gerencia versionamento invisivel por caso.
"""
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class GitCommit:
    """Representa um commit Git."""
    hash: str
    short_hash: str
    message: str
    timestamp: str
    author: str


class GitStateBackend:
    """
    Backend de estado baseado em Git para casos juridicos.

    Cada caso tem seu proprio repositorio Git isolado para:
    - Versionamento automatico de documentos
    - Historico auditavel de mudancas
    - Rollback de estado
    """

    GITIGNORE_CONTENT = """\
# Cache e temporarios
__pycache__/
*.pyc
.DS_Store
*.tmp
*.temp

# Contexto RAG (pode ser grande)
.context/

# Logs de debug
*.log

# Editor configs
.vscode/
.idea/
"""

    def __init__(self, repo_path: Path):
        """
        Inicializa o backend Git.

        Args:
            repo_path: Caminho do diretorio do caso (sera o repo)
        """
        self.repo_path = Path(repo_path)
        self._git_available = self._check_git_available()
        self._ensure_initialized()

    def _check_git_available(self) -> bool:
        """Verifica se git esta disponivel no sistema."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _run_git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """Executa comando git no diretorio do repo."""
        cmd = ["git"] + list(args)
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check
        )

    def _ensure_initialized(self) -> None:
        """Inicializa repositorio Git se nao existir."""
        if not self._git_available:
            print(
                "[WARN] Git nao disponivel. Versionamento desabilitado.",
                file=sys.stderr
            )
            return

        git_dir = self.repo_path / ".git"
        if git_dir.exists():
            return

        # Criar diretorio se nao existir
        self.repo_path.mkdir(parents=True, exist_ok=True)

        # Inicializar repo
        self._run_git("init")

        # Configurar usuario local para commits automaticos
        self._run_git("config", "user.email", "legal-adk@local")
        self._run_git("config", "user.name", "Legal ADK Agent")

        # Criar .gitignore
        self._setup_gitignore()

        # Commit inicial
        self._run_git("add", ".gitignore")
        self._run_git("commit", "-m", "[INIT] Caso juridico inicializado")

    def _setup_gitignore(self) -> None:
        """Cria arquivo .gitignore padrao."""
        gitignore_path = self.repo_path / ".gitignore"
        gitignore_path.write_text(self.GITIGNORE_CONTENT)

    @property
    def is_available(self) -> bool:
        """Retorna se o backend Git esta disponivel."""
        return self._git_available

    def add_all(self) -> bool:
        """Adiciona todas as mudancas ao staging."""
        if not self._git_available:
            return False

        try:
            self._run_git("add", "-A")
            return True
        except subprocess.CalledProcessError:
            return False

    def has_changes(self) -> bool:
        """Verifica se ha mudancas para commitar."""
        if not self._git_available:
            return False

        result = self._run_git("status", "--porcelain", check=False)
        return bool(result.stdout.strip())

    def commit(
        self,
        message: str,
        auto: bool = False,
        phase: Optional[str] = None
    ) -> Optional[str]:
        """
        Cria commit com as mudancas atuais.

        Args:
            message: Mensagem do commit
            auto: Se True, adiciona prefixo [AUTO]
            phase: Fase do pipeline (adiciona ao prefixo)

        Returns:
            Hash do commit ou None se falhar
        """
        if not self._git_available:
            return None

        # Construir prefixo
        prefix_parts = []
        if auto:
            prefix_parts.append("AUTO")
        if phase:
            prefix_parts.append(phase.upper())

        prefix = f"[{'/'.join(prefix_parts)}] " if prefix_parts else ""
        full_message = f"{prefix}{message}"

        # Adicionar mudancas
        self.add_all()

        if not self.has_changes():
            return None

        try:
            self._run_git("commit", "-m", full_message)
            # Retornar hash do commit
            result = self._run_git("rev-parse", "HEAD")
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_history(self, limit: int = 20) -> List[GitCommit]:
        """
        Retorna historico de commits.

        Args:
            limit: Numero maximo de commits

        Returns:
            Lista de GitCommit
        """
        if not self._git_available:
            return []

        try:
            result = self._run_git(
                "log",
                f"-{limit}",
                "--format=%H|%h|%s|%aI|%an",
                check=False
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append(GitCommit(
                        hash=parts[0],
                        short_hash=parts[1],
                        message=parts[2],
                        timestamp=parts[3],
                        author=parts[4]
                    ))

            return commits

        except subprocess.CalledProcessError:
            return []

    def get_file_at_commit(self, filepath: str, commit_hash: str) -> Optional[str]:
        """
        Retorna conteudo de arquivo em um commit especifico.

        Args:
            filepath: Caminho relativo do arquivo
            commit_hash: Hash do commit

        Returns:
            Conteudo do arquivo ou None
        """
        if not self._git_available:
            return None

        try:
            result = self._run_git("show", f"{commit_hash}:{filepath}")
            return result.stdout
        except subprocess.CalledProcessError:
            return None

    def restore_file(self, filepath: str, commit_hash: str) -> bool:
        """
        Restaura arquivo de um commit especifico.

        Args:
            filepath: Caminho relativo do arquivo
            commit_hash: Hash do commit

        Returns:
            True se sucesso
        """
        if not self._git_available:
            return False

        try:
            self._run_git("checkout", commit_hash, "--", filepath)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_diff(self, commit1: Optional[str] = None, commit2: Optional[str] = None) -> str:
        """
        Retorna diff entre commits.

        Args:
            commit1: Commit inicial (HEAD~1 se None)
            commit2: Commit final (HEAD se None)

        Returns:
            Diff em formato texto
        """
        if not self._git_available:
            return ""

        args = ["diff"]
        if commit1:
            args.append(commit1)
        if commit2:
            args.append(commit2)

        try:
            result = self._run_git(*args, check=False)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def create_tag(self, tag_name: str, message: Optional[str] = None) -> bool:
        """
        Cria tag no commit atual.

        Args:
            tag_name: Nome da tag
            message: Mensagem da tag (opcional)

        Returns:
            True se sucesso
        """
        if not self._git_available:
            return False

        try:
            if message:
                self._run_git("tag", "-a", tag_name, "-m", message)
            else:
                self._run_git("tag", tag_name)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do status do repositorio.

        Returns:
            Dict com informacoes de status
        """
        if not self._git_available:
            return {"available": False}

        try:
            # Status
            status_result = self._run_git("status", "--porcelain", check=False)
            changed_files = [
                line.strip()
                for line in status_result.stdout.split("\n")
                if line.strip()
            ]

            # Ultimo commit
            log_result = self._run_git(
                "log", "-1", "--format=%H|%h|%s|%aI",
                check=False
            )
            last_commit = None
            if log_result.returncode == 0 and log_result.stdout.strip():
                parts = log_result.stdout.strip().split("|", 3)
                if len(parts) == 4:
                    last_commit = {
                        "hash": parts[0],
                        "short_hash": parts[1],
                        "message": parts[2],
                        "timestamp": parts[3]
                    }

            # Contagem de commits
            count_result = self._run_git("rev-list", "--count", "HEAD", check=False)
            commit_count = int(count_result.stdout.strip()) if count_result.returncode == 0 else 0

            return {
                "available": True,
                "has_changes": len(changed_files) > 0,
                "changed_files": changed_files,
                "last_commit": last_commit,
                "commit_count": commit_count,
                "repo_path": str(self.repo_path)
            }

        except Exception as e:
            return {
                "available": True,
                "error": str(e)
            }

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emite evento Git para o frontend via stdout.

        Args:
            event_type: Tipo do evento (git_commit, git_status, etc)
            data: Dados do evento
        """
        import json
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        print(f"__ADK_EVENT__{json.dumps(event, ensure_ascii=False)}__ADK_EVENT__", flush=True)
