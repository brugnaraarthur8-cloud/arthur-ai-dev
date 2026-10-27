"""Testes locais sem acesso a APIs, empresas ou sistemas externos."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from arthur.portfolio.monitor_inbox.main import COLUNAS, processar, validar


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

    def test_rejeita_tipos_nao_textuais_em_todos_os_campos(self) -> None:
        for campo in COLUNAS:
            for valor in (None, {}, [], False, 42, 1.5):
                with self.subTest(campo=campo, valor=valor):
                    with self.assertRaisesRegex(ValueError, "deve ser texto"):
                        validar(dict(self.evento, **{campo: valor}))

    def test_exige_data_canonica_e_real(self) -> None:
        for data in ("20261018", "2026-W42-7", "2026-2-03", "2026-02-29", "2026-10-18T00:00:00"):
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
                validar(dict(self.evento, data_solicitacao=data))
        self.assertEqual(validar(dict(self.evento, data_solicitacao="2024-02-29"))["data_solicitacao"], "2024-02-29")

    def test_rejeita_formulas_e_controles_em_todos_os_campos(self) -> None:
        for campo in COLUNAS:
            for valor in ("=1+1", " +1", "-1", "@SUM(1)", "＝1+1", "＋1", "－1", "＠SUM(1)", "\t=1+1", "\r=1+1", "\n=1+1", "texto\x00", "texto\x7f"):
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    validar(dict(self.evento, **{campo: valor}))

    def test_lote_invalido_preserva_saida_inteira(self) -> None:
        self.escrever([self.evento])
        processar(self.entrada, self.saida)
        anterior = self.saida.read_bytes()
        for alteracao in ({"nome": None}, {"nome": "=1+1"}, {"data_solicitacao": "20261018"}):
            with self.subTest(alteracao=alteracao):
                self.escrever([dict(self.evento, protocolo="EXEMPLO-2"), dict(self.evento, **alteracao)])
                with self.assertRaises(ValueError):
                    processar(self.entrada, self.saida)
                self.assertEqual(anterior, self.saida.read_bytes())
                self.assertEqual(list(self.pasta.glob(".arthur-*.csv")), [])

    def test_entrada_invalida_nao_cria_saida(self) -> None:
        self.escrever([dict(self.evento, nome="=1+1")])
        with self.assertRaises(ValueError):
            processar(self.entrada, self.saida)
        self.assertFalse(self.saida.exists())

    def test_csv_malformado_nao_e_reescrito(self) -> None:
        cabecalho = ",".join(COLUNAS) + "\n"
        for registro in (
            "OLD,2026-10-17,Pessoa,Empresa,Teste,pendente,obs,EXTRA\n",
            "OLD,2026-10-17,Pessoa\n",
            'OLD,2026-10-17,"aspas sem fechamento\n',
            "OLD,2026-10-17,=1+1,Empresa,Teste,pendente,obs\n",
            "OLD,20261017,Pessoa,Empresa,Teste,pendente,obs\n",
            ",2026-10-17,Pessoa,Empresa,Teste,pendente,obs\n",
            "OLD,2026-10-17,Pessoa,Empresa,Teste,pendente,obs\nold,2026-10-17,Pessoa,Empresa,Teste,pendente,obs\n",
        ):
            with self.subTest(registro=registro):
                self.saida.write_text(cabecalho + registro, encoding="utf-8-sig")
                anterior = self.saida.read_bytes()
                self.escrever([self.evento])
                with self.assertRaises(ValueError):
                    processar(self.entrada, self.saida)
                self.assertEqual(anterior, self.saida.read_bytes())

    def test_preserva_valores_validos_e_normaliza_chave_existente(self) -> None:
        antiga = dict.fromkeys(COLUNAS, "")
        antiga.update(self.evento, protocolo=" exemplo-1 ", nome='Pessoa, "Fictícia"', observacao="texto com acentuação")
        with self.saida.open("w", encoding="utf-8-sig", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
            escritor.writeheader()
            escritor.writerow(antiga)
        self.escrever([self.evento])
        self.assertEqual(processar(self.entrada, self.saida), 0)
        with self.saida.open(encoding="utf-8-sig", newline="") as arquivo:
            self.assertEqual(list(csv.DictReader(arquivo)), [antiga])

    def test_falha_de_substituicao_preserva_saida_e_remove_temporario(self) -> None:
        self.escrever([self.evento])
        processar(self.entrada, self.saida)
        anterior = self.saida.read_bytes()
        self.escrever([dict(self.evento, protocolo="EXEMPLO-2")])
        with patch("arthur.portfolio.monitor_inbox.main.os.replace", side_effect=OSError("falha simulada")):
            with self.assertRaises(OSError):
                processar(self.entrada, self.saida)
        self.assertEqual(anterior, self.saida.read_bytes())
        self.assertEqual(list(self.pasta.glob(".arthur-*.csv")), [])


if __name__ == "__main__":
    unittest.main()
