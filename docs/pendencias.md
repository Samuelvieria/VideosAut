---
projeto: Canal de Sono Automatizado
assunto: pendências encontradas ao reconciliar com os 26 commits puxados do GitHub
data: 2026-09-03
---

# Pendências

Achados ao puxar (`git pull --ff-only`) e revisar os 26 commits que chegaram de
outra sessão/máquina antes desta. Fast-forward puro, sem conflito de merge — as
duas pendências abaixo são coisas erradas ou ambíguas no que chegou, não
divergência entre versões.

## 1. Bug: `YOUTUBE_API_KEY` duplicada em `pipeline/config.py`

`_FORMATO` tem a chave `"YOUTUBE_API_KEY"` duas vezes:

```python
_FORMATO = {
    "FAL_KEY":           (r"[0-9a-f-]{36}:[0-9a-f]{32}", "uuid:hex, 69 chars"),
    "YOUTUBE_API_KEY":   (r"AIza[A-Za-z0-9_\-]{30,}", "começa com AIza"),
    "YOUTUBE_API_KEY":                "YouTube — só dados PÚBLICOS (não lê analytics)",
    "YOUTUBE_OAUTH_CLIENT":           "YouTube — caminho do JSON do cliente OAuth (lê o seu canal)",
    "ANTHROPIC_API_KEY": (r"sk-ant-[A-Za-z0-9_\-]{20,}", "começa com sk-ant-"),
    "OPENAI_API_KEY":    (r"sk-[A-Za-z0-9_\-]{20,}", "começa com sk-"),
}
```

Python aceita chave duplicada em dict literal e só mantém a última — a tupla de
regex `(r"AIza...", "começa com AIza")` é descartada, e `_FORMATO["YOUTUBE_API_KEY"]`
vira a STRING de descrição (que devia estar só em `_CONHECIDAS`, não aqui).
Confirmado rodando de verdade:

```
>>> _FORMATO['YOUTUBE_API_KEY']
'YouTube — só dados PÚBLICOS (não lê analytics)'
```

**Impacto:** `_valida()` faz `esperado[0]` / `esperado[1]` esperando uma tupla
`(regex, descrição_do_formato)`. Numa string, `esperado[0]` é só o primeiro
caractere ("Y"). Quem rodar `python -m pipeline.config set YOUTUBE_API_KEY` e
colar uma chave real de verdade (`AIza...`) recebe um erro de formato sem
sentido, comparando o valor contra `"Y"`.

`YOUTUBE_OAUTH_CLIENT` também não devia estar em `_FORMATO` — é caminho de
arquivo, como `GOOGLE_APPLICATION_CREDENTIALS`, que tem tratamento próprio em
`_valida()` (branch `if nome == "GOOGLE_APPLICATION_CREDENTIALS"`, resolve o
path e confere se existe). `YOUTUBE_OAUTH_CLIENT` não tem essa branch — hoje
não seria resolvido pra path absoluto nem teria a existência conferida.

**Fix (não aplicado ainda, só diagnosticado):**
1. Remover a linha duplicada de `YOUTUBE_API_KEY` em `_FORMATO`, mantendo só a
   tupla de regex.
2. Remover `YOUTUBE_OAUTH_CLIENT` de `_FORMATO` inteiramente.
3. Estender a branch de path em `_valida()` pra tratar `GOOGLE_APPLICATION_CREDENTIALS`
   e `YOUTUBE_OAUTH_CLIENT` igual (mesmo tipo de segredo: caminho de JSON).

Nem `YOUTUBE_API_KEY` nem `YOUTUBE_OAUTH_CLIENT` estão preenchidas no `.env`
local — o bug ainda não foi exercitado na prática aqui.

## 2. video-02: publicado ou pendente de re-render?

`fase0/video-02/README.md` tem duas seções que não batem:

- `## PUBLICADO em 03/09/2026` — com URL real (`youtube.com/watch?v=103_aYlJr4o`),
  canal SleepPowder.
- `## Estado (03/09/2026)` — lista `[ ] Render final — refazer, tudo mudou
  desde o último` e `[ ] Upload manual` como pendentes.

Note no fim do arquivo: *"Antes de renderizar na workstation: git pull. Os
últimos commits mudaram a resolução das imagens, o alvo de duração e a
abertura do roteiro."* — ou seja, o vídeo publicado pode ser uma versão
anterior à correção de resolução (1280×720, ver `CLAUDE.md` § Imagens) e à
mudança de duração/abertura, e o que está publicado no YouTube agora pode não
bater com o que os arquivos locais descrevem.

**Não resolvido aqui** — precisa confirmar com o Samuel qual dos dois estados é
real antes de tocar em render ou upload do video-02.
