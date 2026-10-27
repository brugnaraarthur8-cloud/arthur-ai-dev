# Arthur AI Dev: instalação e testes no Windows

Esta é uma personalização adicional do fork de `miuuyy/codex-chatgpt-web`. Ela não substitui o launcher.

## Requisitos
- Windows e Python 3.11 ou superior para os exemplos de portfólio.
- Git para baixar as alterações da sua conta GitHub.
- Para desenvolver o projeto TypeScript original: Bun 1.4.0 (exigido pelo upstream).

## 1. Obter o projeto e a personalização

```powershell
git clone https://github.com/brugnaraarthur8-cloud/arthur-ai-dev.git
cd arthur-ai-dev
git fetch origin
git switch feature/arthur-ai-dev
```

Para usar a personalização na branch principal, revise e faça merge do Pull Request antes de fazer o clone.

## 2. Teste rápido

Na raiz do repositório execute:

```powershell
python -m arthur.cli perfis
python -m arthur.cli prompt agentes
python -m arthur.portfolio.monitor_inbox.main --entrada arthur/portfolio/monitor_inbox/exemplo.json --saida saida/solicitacoes.csv
python -m unittest discover -s arthur/portfolio/monitor_inbox/tests -v
```

Os comandos acima não exigem login, chaves nem acesso à internet. Não use dados corporativos.

## 3. Git e arquivos gerados

O arquivo `saida/solicitacoes.csv` é gerado localmente. O `.gitignore` já cobre `saida/`, `.venv/`, caches Python, `.env.arthur` e `arthur-secrets/`. Isso não remove arquivos já rastreados nem substitui a revisão do diff. Nunca publique arquivos de sessão do ChatGPT ou chaves da API.

## 4. Launcher do upstream

Para rodar o launcher, siga o `README.md` da base original. Comece com Browser-only; revise `docs/security-model.md` antes de configurar MCP. A integração de navegador é não oficial e não equivale a API de produção.

## 5. Próximos projetos

- Automação de e-mails de uma caixa de testes, com autenticação oficial.
- Agente que responde com citações de documentos fictícios.
- Integrações n8n com API oficial, logs e aprovações de ações externas.
