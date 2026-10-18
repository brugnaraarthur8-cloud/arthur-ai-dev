# Monitor de solicitações sintéticas

Exemplo **funcional, local e sem acesso a redes** para um portfólio de automação. Converte um JSON de solicitações inventadas em CSV. Reexecutar não duplica os mesmos protocolos.

```powershell
python -m arthur.portfolio.monitor_inbox.main --entrada arthur/portfolio/monitor_inbox/exemplo.json --saida saida/solicitacoes.csv
python -m unittest discover -s arthur/portfolio/monitor_inbox/tests -v
```

- Entrada: lista JSON com `protocolo`, `data_solicitacao` (`YYYY-MM-DD`), `nome` e `servico` obrigatórios.
- Saída: CSV codificado em UTF-8 com BOM, compatível com Excel Windows.
- Segurança: valida antes de escrever, não usa credenciais, preserva registros e evita duplicidade por protocolo (sem diferenciação de maiúsculas/minúsculas).
- Limite: não faz processamento simultâneo do mesmo arquivo, integração de e-mail nem conciliação de alterações já gravadas.
