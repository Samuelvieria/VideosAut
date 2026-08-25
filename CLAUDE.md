# Contexto do projeto — Canal de Sono Automatizado

Análise completa em [docs/viabilidade-tecnica.md](docs/viabilidade-tecnica.md). Resumo das
decisões de arquitetura já tomadas — não reabrir essas discussões sem motivo novo:

## Decisões fixadas

- **Zero editor de vídeo.** Um vídeo de sono é 1 imagem/loop curto + 1 trilha de áudio longa.
  Tudo em FFmpeg puro (render, mix de áudio, concat). Nada de DaVinci/Premiere/CapCut.
- **Claude Code é o engenheiro, não o servidor de produção.** Quem roda em produção é um
  pipeline Python + cron, determinístico e idempotente. Claude (API, não Claude Code) só
  gera o estágio criativo (roteiro/metadados) dentro do pipeline.
- **Sem prompt fixo.** Banco de premissas + 5–8 estruturas narrativas sorteadas por vídeo,
  para não cair em "conteúdo inautêntico" (política do YouTube desde jul/2025).
- **Cadência humana: 2–3 vídeos/semana**, nunca 7. Volume alto + formato idêntico é o sinal
  de risco mais forte.
- **Gate manual obrigatório antes de publicar.** Todo upload sobe como `private`; você aprova
  antes de tornar público. Isso também contorna a trava automática de vídeos como privados
  em projetos de API não auditados (armadilha nº1 da seção 5).
- **Áudio ambiente gerado proceduralmente** (brown/pink noise via FFmpeg `anoisesrc`), nunca
  música de terceiros sem whitelist de Content ID. É a única fonte impossível de dar match.
- **Legendas sempre soft (`captions.insert`), nunca queimadas** — permite multi-idioma sem
  re-renderizar e não atrapalha o objetivo do conteúdo (texto na tela é contraproducente
  em vídeo de sono).
- **Divulgação de conteúdo sintético ativada** para voz/imagem geradas (toggle no Studio).

## Não pular a Fase 0

O maior risco do projeto não é técnico — é construir automação eficiente demais para um
produto não validado. Não escrever `s1_roteiro.py`/`s6_upload.py` antes de ter 2–3 vídeos
manuais publicados e alguma leitura de retenção/audiência.

## Itens não verificados (não assumir como fato)

Ver seção 10 do documento de viabilidade — custo de quota de `videos.insert`/`captions.insert`,
nome exato do campo de divulgação sintética na Data API v3, comportamento de loudness do
YouTube, expiração de refresh token OAuth. Confirmar na documentação oficial antes de
depender desses valores em código.

## Estrutura do repositório

Ainda em Fase 0 — sem pipeline/scripts. Estrutura cresce por fase (ver README.md).
`output/` e `state/` (quando existirem) são gerados localmente e não versionados.
