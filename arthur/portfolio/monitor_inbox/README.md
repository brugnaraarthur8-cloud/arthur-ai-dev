# Monitor de solicitações sintéticas

Exemplo **funcional, local e sem acesso a redes** para um portfólio de automação. Converte um JSON de solicitações inventadas em CSV. Reexecutar não duplica os mesmos protocolos.

```powershell
python -m arthur.portfolio.monitor_inbox.main --entrada arthur/portfolio/monitor_inbox/exemplo.json --saida saida/solicitacoes.csv
python -m unittest discover -s arthur/portfolio/monitor_inbox/tests -v
```

- Entrada: lista JSON com `protocolo`, `data_solicitacao` (`YYYY-MM-DD`), `nome` e `servico` obrigatórios.
- Todos os campos devem ser strings. Campos opcionais ausentes recebem texto vazio; `null`, números, listas e objetos são rejeitados. Datas precisam ter o formato exato e existir no calendário.
- Os campos são de linha única, sem caracteres de controle. Para impedir fórmulas em planilhas, valores que começam com `=`, `+`, `-` ou `@` (incluindo variantes de largura completa e após espaços) são rejeitados, sem alteração silenciosa dos dados.
- Saída: CSV codificado em UTF-8 com BOM, compatível com Excel Windows.
- Segurança: valida antes de escrever, não usa credenciais, preserva registros e evita duplicidade por protocolo (sem diferenciação de maiúsculas/minúsculas).
- O CSV existente também é validado: cabeçalho, número de campos, conteúdo, aspas e protocolos duplicados. Em caso de erro, o arquivo original permanece intacto. Valores válidos existentes são preservados; espaços externos no protocolo não criam outra identidade.
- Limite: não faz processamento simultâneo do mesmo arquivo, integração de e-mail nem conciliação de alterações já gravadas.
