# Canal de Sono Automatizado

Pipeline para um canal de conteúdo para dormir (sleep stories / ambiente sonoro) no YouTube.

Ver [docs/viabilidade-tecnica.md](docs/viabilidade-tecnica.md) para a análise completa de
arquitetura, custos e riscos de política do YouTube. Contexto persistente para trabalho
com Claude Code em [CLAUDE.md](CLAUDE.md).

## Status atual

**Fase 0 — validação manual.** Produzindo os primeiros 2–3 vídeos inteiramente à mão
(roteiro, TTS, render) antes de automatizar qualquer etapa. Objetivo: descobrir o que
retém público antes de construir uma fábrica de conteúdo que ninguém assiste.

## Interface

[estudio/](estudio/README.md) — app web local (FastAPI) pra acompanhar projetos,
personas e disparar estágios do pipeline sem linha de comando. Ainda não faz roteiro
por LLM nem upload; ver o README dele pro que existe e o porquê dos limites.

## Roadmap

| Fase | Escopo |
|---|---|
| 0 (atual) | 3 vídeos 100% manuais |
| 1 | Automatizar TTS + render (`s2_tts.py`, `s5_render.py`) |
| 2 | Roteiro via API + banco de premissas |
| 3 | Upload automático (sempre `private`) + gate manual |
| 4 | Legendas multi-idioma |
| 5 | Auditoria da API do YouTube |
