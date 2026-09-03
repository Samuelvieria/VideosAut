# Pipeline

Estágios determinísticos e idempotentes. **Nenhum LLM roda aqui dentro** — ver
seção 2.1 do doc de viabilidade. Rodar duas vezes com a mesma entrada dá o mesmo
resultado e não refaz trabalho.

```
python -m pipeline.s2_tts       fase0/video-02
python -m pipeline.s3_imagens   fase0/video-02
python -m pipeline.s5_render    fase0/video-02
python -m pipeline.s4_legendas  fase0/video-02
```

| Estágio | Entrada | Saída |
|---|---|---|
| `s2_tts` | `roteiro.md`, bloco `voz` do `plano.json` | `audio/cena_NN.wav`, `duracoes.json` |
| `s3_imagens` | `plano.json` (`estilo_base` + prompt por cena), `FAL_KEY` | `imagens/cena_NN.png` (640×360) |
| `s5_render` | `imagens/`, `audio/`, `plano.json` | `final.mp4` |
| `s7_auth` | JSON do cliente OAuth | `~/.config/youtube-token.json` |
| `s7_metricas` | token + ID do vídeo | relatório no terminal, `metricas/*.json` |
| `s4_legendas` | `audio/`, `roteiro.md` | `legendas.pt-BR.srt` |

`comum.py` tem a infraestrutura: wrapper de ffmpeg que aborta no erro, `ffprobe`,
escape de path para o concat demuxer, e o par `atualizado()`/`marcar()` que dá a
idempotência (grava hash das entradas ao lado da saída).

## O que NÃO existe aqui, de propósito

`s1_roteiro.py` (roteiro por LLM) e `s6_upload.py` (publicação). O CLAUDE.md os
proíbe antes de 2–3 vídeos manuais publicados. O risco do projeto não é técnico —
é construir uma fábrica eficiente para um produto não validado.

## Decisões travadas nestes scripts

- **O áudio manda no corte.** A duração de cada cena vem do `.wav` dela, não do
  plano. `plano.json` traz alvos; o render usa o real.
- **Um clipe por cena, `concat -c copy` no fim.** Sem reencode na montagem.
  Exige GOP fechado e alinhado (`-g 48 -keyint_min 48 -sc_threshold 0` a 24 fps).
- **`-t` é opção de saída.** Antes do `-i` o comando gera milhões de frames e
  nunca termina. Já custou 8 min de render travado uma vez.
- **`scale=...:flags=neighbor`.** Upscale de pixel art tem que ser nearest e em
  escala inteira (640×360 ×3 = 1920×1080). Qualquer interpolação borra a grade.
- **Movimento por passo inteiro, não Ken Burns.** Ken Burns/`zoompan` ingênuo
  reamostra em subpixel e destrói a grade de pixel art. Implementado em
  27/08/2026: `crop` (nunca reamostra) corta uma janela menor que os 640×360
  gerados e desliza por pixel inteiro da fonte; o `scale=neighbor` que segue
  continua um fator inteiro exato (×4) até 1920×1080. Cauda sem narração fica
  parada — ver `clipe_cena` em `s5_render.py`.
- **Legenda soft.** `s4` gera `.srt` para `captions.insert`. Nunca queimar.
- **Mix a −14 LUFS integrado / teto real −1 dBTP** (era −18, deliberadamente abaixo, até
  28/08/2026) — é o alvo real de normalização do YouTube; entregar mais baixo só
  faz o espectador subir o volume do aparelho e levar um susto no próximo
  vídeo/anúncio, normalizado em −14. O `TP` passado ao `loudnorm` é **−1,5**, não
  −1,0: o loudnorm (mesmo em 2 passos linear) overshoot o TP pedido em ~0,1-0,4dB
  na prática — medido no video-02, pedir −1,0 mediu −0,88 (passou do teto real do
  checklist); pedir −1,5 mediu −1,40, com margem. Ver `pipeline.s5_render.MASTER_TP`.
  Masterização em **2 passos com `loudnorm=...:linear=true`**, nunca 1 passo
  dinâmico no mix já somado — dinâmico reage à loudness corrente e reinfla o
  volume geral (ambiente incluso) sempre que a soma fica baixa, desfazendo o ganho
  calibrado no mixer. Ver `_masterizar_2passos()`. Ducking sidechain do ambiente
  pela narração continua, com redução mais suave (4-6dB, não 10+) e release mais
  longo (1,5-3s) — ver `.claude/skills/qualidade-producao-video/SKILL.md`.
