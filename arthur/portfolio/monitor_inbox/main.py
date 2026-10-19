"""Transforma solicitações sintéticas JSON em CSV de forma idempotente.

Uso: python -m arthur.portfolio.monitor_inbox.main --entrada ... --saida ...
Nunca lê e-mails reais, redes nem dados corporativos.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

COLUNAS = ("protocolo", "data_solicitacao", "nome", "empresa", "servico", "status", "observacao")


def validar(evento: Any) -> dict[str, str]:
    if not isinstance(evento, dict):
        raise ValueError("Cada solicitação deve ser um objeto JSON")
    linha = {campo: str(evento.get(campo, "")).strip() for campo in COLUNAS}
    obrigatorios = ("protocolo", "data_solicitacao", "nome", "servico")
    vazios = [campo for campo in obrigatorios if not linha[campo]]
    if vazios:
        raise ValueError("Campos obrigatórios ausentes: " + ", ".join(vazios))
    try:
        date.fromisoformat(linha["data_solicitacao"])
    except ValueError as exc:
        raise ValueError("data_solicitacao deve estar em YYYY-MM-DD") from exc
    linha["status"] = linha["status"] or "pendente"
    return linha


def carregar_eventos(caminho: Path) -> list[dict[str, str]]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if not isinstance(dados, list):
        raise ValueError("Arquivo de entrada deve conter lista de solicitações")
    return [validar(item) for item in dados]


def carregar_existentes(caminho: Path) -> list[dict[str, str]]:
    if not caminho.exists():
        return []
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != list(COLUNAS):
            raise ValueError("CSV existente não tem as colunas esperadas; nenhuma alteração foi feita")
        return [{campo: linha[campo] for campo in COLUNAS} for linha in leitor]


def mesclar(existentes: list[dict[str, str]], novos: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    protocolos = {linha["protocolo"].casefold() for linha in existentes}
    resultado = list(existentes)
    adicionados = 0
    for linha in novos:
        chave = linha["protocolo"].casefold()
        if chave not in protocolos:
            resultado.append(linha)
            protocolos.add(chave)
            adicionados += 1
    return resultado, adicionados


def salvar_csv_atomico(caminho: Path, linhas: list[dict[str, str]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", dir=caminho.parent,
                                         prefix=".arthur-", suffix=".csv", delete=False) as arquivo:
            temporario = arquivo.name
            writer = csv.DictWriter(arquivo, fieldnames=COLUNAS)
            writer.writeheader()
            writer.writerows(linhas)
        os.replace(temporario, caminho)
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)


def processar(entrada: Path, saida: Path) -> int:
    # Valida todos os eventos ANTES de modificar a saída.
    eventos = carregar_eventos(entrada)
    existentes = carregar_existentes(saida)
    linhas, quantidade = mesclar(existentes, eventos)
    salvar_csv_atomico(saida, linhas)
    return quantidade


def main() -> None:
    parser = argparse.ArgumentParser(description="Automação local de portfólio: JSON → CSV")
    parser.add_argument("--entrada", required=True, type=Path)
    parser.add_argument("--saida", required=True, type=Path)
    args = parser.parse_args()
    try:
        quantidade = processar(args.entrada, args.saida)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Erro: {exc}\n")
    print(f"Concluído: {quantidade} solicitações novas, saída: {args.saida}")


if __name__ == "__main__":
    main()
