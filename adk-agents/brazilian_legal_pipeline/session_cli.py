#!/usr/bin/env python3
"""
CLI para gerenciamento de sessoes do Legal Pipeline.
Projetado para ser invocado pelo Tauri via shell.

Uso:
    python -m brazilian_legal_pipeline.session_cli start --case-path /path --case-id id
    python -m brazilian_legal_pipeline.session_cli resume --case-path /path
    python -m brazilian_legal_pipeline.session_cli run --session-id xxx --consultation '{...}'
    python -m brazilian_legal_pipeline.session_cli status --session-id xxx
    python -m brazilian_legal_pipeline.session_cli pause --session-id xxx
    python -m brazilian_legal_pipeline.session_cli stop --session-id xxx
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar parent ao path para imports relativos
sys.path.insert(0, str(Path(__file__).parent.parent))

from brazilian_legal_pipeline.session_manager import get_session_manager, SessionInfo
from brazilian_legal_pipeline.git_state import GitStateBackend


def emit_event(event_type: str, data: dict) -> None:
    """Emite evento no formato esperado pelo frontend."""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    print(f"__ADK_EVENT__{json.dumps(event, ensure_ascii=False)}__ADK_EVENT__", flush=True)


def emit_result(success: bool, data: dict = None, error: str = None) -> None:
    """Emite resultado final da operacao."""
    result = {
        "success": success,
        "data": data,
        "error": error
    }
    emit_event("cli_result", result)


async def cmd_start(args: argparse.Namespace) -> int:
    """Inicia nova sessao."""
    try:
        manager = get_session_manager()

        emit_event("cli_starting", {
            "command": "start",
            "case_path": args.case_path,
            "case_id": args.case_id
        })

        session = await manager.create_session(
            case_path=args.case_path,
            case_id=args.case_id
        )

        emit_result(True, session.to_dict())
        return 0

    except PermissionError as e:
        emit_result(False, error=f"Permissao negada: {e}")
        return 1
    except ValueError as e:
        emit_result(False, error=f"Caminho invalido: {e}")
        return 1
    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_resume(args: argparse.Namespace) -> int:
    """Resume sessao existente."""
    try:
        manager = get_session_manager()

        emit_event("cli_starting", {
            "command": "resume",
            "case_path": args.case_path
        })

        session = await manager.resume_session(case_path=args.case_path)

        emit_result(True, session.to_dict())
        return 0

    except FileNotFoundError as e:
        emit_result(False, error=f"Sessao nao encontrada: {e}")
        return 1
    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_run(args: argparse.Namespace) -> int:
    """Executa pipeline em uma sessao."""
    try:
        manager = get_session_manager()

        # Parse consultation JSON
        try:
            consultation = json.loads(args.consultation)
        except json.JSONDecodeError as e:
            emit_result(False, error=f"JSON invalido na consulta: {e}")
            return 1

        emit_event("cli_starting", {
            "command": "run",
            "session_id": args.session_id
        })

        result = await manager.run_pipeline(
            session_id=args.session_id,
            consultation=consultation
        )

        emit_result(True, result.to_dict())
        return 0 if result.success else 1

    except KeyError as e:
        emit_result(False, error=f"Sessao nao encontrada: {e}")
        return 1
    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_start_and_run(args: argparse.Namespace) -> int:
    """Cria sessao e executa pipeline em um comando."""
    try:
        manager = get_session_manager()

        # Parse consultation JSON
        try:
            consultation = json.loads(args.consultation)
        except json.JSONDecodeError as e:
            emit_result(False, error=f"JSON invalido na consulta: {e}")
            return 1

        emit_event("cli_starting", {
            "command": "start-and-run",
            "case_path": args.case_path,
            "case_id": args.case_id
        })

        # Criar sessao
        session = await manager.create_session(
            case_path=args.case_path,
            case_id=args.case_id
        )

        # Executar pipeline
        result = await manager.run_pipeline(
            session_id=session.session_id,
            consultation=consultation
        )

        emit_result(True, {
            "session": session.to_dict(),
            "pipeline_result": result.to_dict()
        })
        return 0 if result.success else 1

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_status(args: argparse.Namespace) -> int:
    """Retorna status de uma sessao."""
    try:
        manager = get_session_manager()
        session = manager.get_session(args.session_id)

        if session:
            # Adicionar status do Git
            git_backend = GitStateBackend(session.case_path)
            git_status = git_backend.get_status_summary()

            emit_result(True, {
                "session": session.to_dict(),
                "git": git_status
            })
            return 0
        else:
            emit_result(False, error=f"Sessao nao encontrada: {args.session_id}")
            return 1

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_pause(args: argparse.Namespace) -> int:
    """Pausa pipeline em execucao."""
    try:
        manager = get_session_manager()
        success = await manager.pause_pipeline(args.session_id)

        if success:
            emit_result(True, {"action": "paused", "session_id": args.session_id})
            return 0
        else:
            emit_result(False, error="Nao foi possivel pausar (pipeline nao encontrado)")
            return 1

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_resume_pipeline(args: argparse.Namespace) -> int:
    """Resume pipeline pausado."""
    try:
        manager = get_session_manager()
        success = await manager.resume_pipeline(args.session_id)

        if success:
            emit_result(True, {"action": "resumed", "session_id": args.session_id})
            return 0
        else:
            emit_result(False, error="Nao foi possivel resumir (pipeline nao encontrado)")
            return 1

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_stop(args: argparse.Namespace) -> int:
    """Para pipeline em execucao."""
    try:
        manager = get_session_manager()
        success = await manager.stop_pipeline(args.session_id)

        if success:
            emit_result(True, {"action": "stopped", "session_id": args.session_id})
            return 0
        else:
            emit_result(False, error="Nao foi possivel parar (pipeline nao encontrado)")
            return 1

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_list(args: argparse.Namespace) -> int:
    """Lista sessoes ativas."""
    try:
        manager = get_session_manager()
        sessions = manager.list_sessions()

        emit_result(True, {
            "sessions": [s.to_dict() for s in sessions],
            "count": len(sessions)
        })
        return 0

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_git_status(args: argparse.Namespace) -> int:
    """Retorna status Git de um caso."""
    try:
        case_path = Path(args.case_path).resolve()
        git_backend = GitStateBackend(case_path)

        status = git_backend.get_status_summary()
        history = git_backend.get_history(limit=args.limit)

        emit_result(True, {
            "status": status,
            "history": [
                {
                    "hash": c.hash,
                    "short_hash": c.short_hash,
                    "message": c.message,
                    "timestamp": c.timestamp,
                    "author": c.author
                }
                for c in history
            ]
        })
        return 0

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


async def cmd_git_commit(args: argparse.Namespace) -> int:
    """Cria commit manual em um caso."""
    try:
        case_path = Path(args.case_path).resolve()
        git_backend = GitStateBackend(case_path)

        commit_hash = git_backend.commit(
            message=args.message,
            auto=False,
            phase=args.phase
        )

        if commit_hash:
            emit_result(True, {"commit_hash": commit_hash})
            return 0
        else:
            emit_result(False, error="Nenhuma mudanca para commitar")
            return 1

    except Exception as e:
        emit_result(False, error=str(e))
        return 1


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="CLI para gerenciamento de sessoes do Legal Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    start_parser = subparsers.add_parser("start", help="Inicia nova sessao")
    start_parser.add_argument("--case-path", required=True, help="Caminho do caso")
    start_parser.add_argument("--case-id", required=True, help="ID do caso")

    # resume
    resume_parser = subparsers.add_parser("resume", help="Resume sessao existente")
    resume_parser.add_argument("--case-path", required=True, help="Caminho do caso")

    # run
    run_parser = subparsers.add_parser("run", help="Executa pipeline")
    run_parser.add_argument("--session-id", required=True, help="ID da sessao")
    run_parser.add_argument("--consultation", required=True, help="JSON da consulta")

    # start-and-run (atalho)
    start_run_parser = subparsers.add_parser(
        "start-and-run",
        help="Cria sessao e executa pipeline"
    )
    start_run_parser.add_argument("--case-path", required=True, help="Caminho do caso")
    start_run_parser.add_argument("--case-id", required=True, help="ID do caso")
    start_run_parser.add_argument("--consultation", required=True, help="JSON da consulta")

    # status
    status_parser = subparsers.add_parser("status", help="Status da sessao")
    status_parser.add_argument("--session-id", required=True, help="ID da sessao")

    # pause
    pause_parser = subparsers.add_parser("pause", help="Pausa pipeline")
    pause_parser.add_argument("--session-id", required=True, help="ID da sessao")

    # resume-pipeline
    resume_p_parser = subparsers.add_parser(
        "resume-pipeline",
        help="Resume pipeline pausado"
    )
    resume_p_parser.add_argument("--session-id", required=True, help="ID da sessao")

    # stop
    stop_parser = subparsers.add_parser("stop", help="Para pipeline")
    stop_parser.add_argument("--session-id", required=True, help="ID da sessao")

    # list
    subparsers.add_parser("list", help="Lista sessoes ativas")

    # git-status
    git_status_parser = subparsers.add_parser("git-status", help="Status Git do caso")
    git_status_parser.add_argument("--case-path", required=True, help="Caminho do caso")
    git_status_parser.add_argument(
        "--limit", type=int, default=10,
        help="Limite de commits no historico"
    )

    # git-commit
    git_commit_parser = subparsers.add_parser("git-commit", help="Commit manual")
    git_commit_parser.add_argument("--case-path", required=True, help="Caminho do caso")
    git_commit_parser.add_argument("--message", "-m", required=True, help="Mensagem do commit")
    git_commit_parser.add_argument("--phase", help="Fase atual (opcional)")

    args = parser.parse_args()

    # Mapear comandos para handlers
    handlers = {
        "start": cmd_start,
        "resume": cmd_resume,
        "run": cmd_run,
        "start-and-run": cmd_start_and_run,
        "status": cmd_status,
        "pause": cmd_pause,
        "resume-pipeline": cmd_resume_pipeline,
        "stop": cmd_stop,
        "list": cmd_list,
        "git-status": cmd_git_status,
        "git-commit": cmd_git_commit,
    }

    handler = handlers.get(args.command)
    if handler:
        exit_code = asyncio.run(handler(args))
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
