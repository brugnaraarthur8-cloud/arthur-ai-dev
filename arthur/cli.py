"""Consulta aos perfis do Arthur AI Dev. Sem dependências externas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PERFIS = {
    "programacao": "programacao.md",
    "automacao": "automacao.md",
    "agentes": "agentes.md",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Perfis Arthur AI Dev")
    parser.add_argument("acao", choices=["perfis", "prompt", "config"])
    parser.add_argument("nome", nargs="?", choices=sorted(PERFIS))
    args = parser.parse_args()

    if args.acao == "perfis":
        print("Perfis disponíveis: " + ", ".join(PERFIS))
    elif args.acao == "config":
        print(json.dumps(json.loads((BASE / "config.json").read_text(encoding="utf-8")), ensure_ascii=False, indent=2))
    else:
        if not args.nome:
            parser.error("Informe um perfil: programacao, automacao ou agentes")
        print((BASE / "prompts" / PERFIS[args.nome]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
