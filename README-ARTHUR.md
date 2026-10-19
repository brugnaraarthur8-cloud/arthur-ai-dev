# Arthur AI Dev 🚀

Personalização independente do fork [miuuyy/codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web), focada em **Python, programação, automações empresariais e agentes de IA**.

> O launcher e o mecanismo Codex continuam sendo os originais. Estes arquivos adicionam instruções e exemplos educacionais, **não** reimplementam nem validam a integração ChatGPT Web.

## O que foi acrescentado

- `AGENTS.md`: instruções de trabalho para o Codex neste repositório.
- `arthur/prompts/`: perfis para programação, automações e agentes.
- `arthur/cli.py`: exibe perfis e configurações.
- `arthur/portfolio/monitor_inbox/`: exemplo local e funcional de JSON para CSV.
- `.github/workflows/arthur-python-tests.yml`: verificações Python automáticas.
- `docs/ARTHUR-INSTALACAO.md`: instruções Windows e próximos passos.

## Comece pelos exemplos (Python 3.11+)

Na raiz do repositório:

```powershell
python -m arthur.cli perfis
python -m arthur.cli prompt automacao
python -m arthur.portfolio.monitor_inbox.main --entrada arthur/portfolio/monitor_inbox/exemplo.json --saida saida/solicitacoes.csv
python -m unittest discover -s arthur/portfolio/monitor_inbox/tests -v
```

Os arquivos gerados localmente ficam em `saida/`, ignorada no Git. O exemplo funciona sem pacotes adicionais, login, API, rede nem dados de clientes.

## Sobre o launcher

Consulte o [README original](README.md) para instalação e uso do launcher (base TypeScript + Bun 1.4.0 para desenvolver a partir do código). A ponte usa automação não oficial do navegador e pode parar de funcionar após atualizações do ChatGPT. Não utilize essa técnica como integração de produção em serviços de clientes. Para automações comerciais, use APIs oficiais e autorização explícita.

## Autoria e licença

Projeto original de [miuuyy/codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web), MIT. Este fork mantém a atribuição, LICENSE e avisos de terceiros. A personalização não é um produto oficial ou endossado pela OpenAI.
