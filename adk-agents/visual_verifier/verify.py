#!/usr/bin/env python3
"""CLI wrapper para Visual Verifier.

Uso direto (sem adk):
    ./verify.py quick https://localhost:3000
    ./verify.py verify https://localhost:3000 homepage
    ./verify.py baseline https://localhost:3000 homepage
    ./verify.py list
"""

import sys
import json
from pathlib import Path

# Adiciona o diretorio atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from agent import verify_page, update_baseline, list_baselines, quick_check


def main():
    if len(sys.argv) < 2:
        print("Uso: verify.py <comando> [args...]")
        print("Comandos: quick, verify, baseline, list")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "quick" and len(sys.argv) >= 3:
        url = sys.argv[2]
        result = quick_check(url)
        print(json.dumps(result, indent=2))

    elif cmd == "verify" and len(sys.argv) >= 4:
        url = sys.argv[2]
        page_name = sys.argv[3]
        result = verify_page(url, page_name)
        print(json.dumps(result, indent=2))

    elif cmd == "baseline" and len(sys.argv) >= 4:
        url = sys.argv[2]
        page_name = sys.argv[3]
        result = update_baseline(url, page_name)
        print(json.dumps(result, indent=2))

    elif cmd == "list":
        result = list_baselines()
        print(json.dumps(result, indent=2))

    else:
        print(f"Comando invalido: {cmd}")
        print("Comandos: quick <url>, verify <url> <name>, baseline <url> <name>, list")
        sys.exit(1)


if __name__ == "__main__":
    main()
