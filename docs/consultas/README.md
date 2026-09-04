# Consultas a modelos externos

Os arquivos em `brutas/` são respostas de modelos externos ao briefing do
projeto, colados à mão. A [síntese](sintese.md) é a leitura cruzada delas.

Desde 04/09/2026 dá para consultar sem copiar e colar.

## Como está ligado

O **Gemini CLI morreu em 18/06/2026** para conta de consumidor — Pro, Ultra e
free tier, os três. Só sobrou licença Code Assist corporativa. O sucessor é o
**Antigravity CLI (`agy`)**, e o plano pago do Samuel dá acesso a modelo Pro
nele.

```bash
brew install --cask antigravity-cli     # já feito; instala /opt/homebrew/bin/agy
agy models                              # diagnóstico, não gasta prompt
```

Modelos disponíveis nesta conta (04/09/2026):

| modelo | nota |
|---|---|
| `gemini-3.1-pro-high` / `-low` | o mais forte da lista |
| `gemini-3.8-flash-high` / `-medium` / `-low` | rápido e barato |
| `gemini-3.7-flash-*`, `gemini-3.6-flash-*` | gerações anteriores |
| `claude-sonnet-4-6`, `claude-opus-4-6-thinking` | via Vertex Model Garden |
| `gpt-oss-120b-medium` | idem |

## Uso

```bash
agy --model gemini-3.1-pro-high -p "PERGUNTA"
agy --model gemini-3.1-pro-high --output-format json -p "PERGUNTA"
cat docs/briefing-externo.md | agy --model gemini-3.1-pro-high -p "Critique isto."
```

`--effort` e o sufixo `-high|-medium|-low` controlam o esforço de raciocínio.
A quota renova a cada cinco horas nos planos pagos.

## Duas regras

**1. Isto envia conteúdo para o Google.** Tudo que entra no prompt sai da
máquina. Não mandar `.env`, chave, nem o `oauth_creds.json`. Quando a consulta
for sobre o projeto, mandar o documento pertinente — não o repositório inteiro.

**2. Pedir segunda opinião a `claude-*` tem valor limitado.** Os modelos Claude
da lista vêm pelo Vertex Model Garden e são da mesma família de quem escreve
este repositório. Para o efeito que a `sintese.md` busca — convergência entre
fontes **independentes** — o valor está em `gemini-3.1-pro` e `gpt-oss-120b`.

## Por que a conta de estudante não servia

O `~/.gemini/oauth_creds.json` estava autenticado como
`...@sga.pucminas.br`, que o servidor reportou como `free-tier` /
"Gemini Code Assist for individuals" — a faixa cortada. O `agy` usa a sessão do
Antigravity, que está na conta com plano pago.
