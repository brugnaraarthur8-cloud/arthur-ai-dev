"""Testes locais sem acesso a APIs, empresas ou sistemas externos."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from arthur.portfolio.monitor_inbox.main import processar, validar


class TestMonitorInbox(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pasta = Path(self.temp.name)
        self.entrada = self.pasta / "entrada.json"
        self.saida = self.pasta / "saida.csv"
        self.evento = {
            "protocolo": "EXEMPLO-1", "data_solicitacao": "2026-10-18",
            "nome": "Pessoa Inventada", "servico": "Teste", "empresa": "Empresa Fake"
        }

    def escrever(self, eventos: list[dict]) -> None:
        self.entrada.write_text(json.dumps(eventos), encoding="utf-8")

    def test_processa_e_nao_duplica(self) -> None:
        self.escrever([self.evento, dict(self.evento, protocolo="exemplo-1")])
        self.assertEqual(processar(self.entrada, self.saida), 1)
        self.assertEqual(processar(self.entrada, self.saida), 0)
        with self.saida.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 1)

    def test_falha_de_validacao_nao_altera_csv(self) -> None:
        self.escrever([self.evento])
        processar(self.entrada, self.saida)
        anterior = self.saida.read_bytes()
        self.escrever([dict(self.evento, data_solicitacao="18/10/2026")])
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            processar(self.entrada, self.saida)
        self.assertEqual(anterior, self.saida.read_bytes())

    def test_exige_campos_obrigatorios(self) -> None:
        with self.assertRaisesRegex(ValueError, "Campos obrigatórios"):
            validar({"protocolo": "ABC"})

    def test_preserva_linhas_anteriores(self) -> None:
        self.escrever([self.evento])
        processar(self.entrada, self.saida)
        self.escrever([dict(self.evento, protocolo="EXEMPLO-2")])
        self.assertEqual(processar(self.entrada, self.saida), 1)
        with self.saida.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 2)


if __name__ == "__main__":
    unittest.main()
