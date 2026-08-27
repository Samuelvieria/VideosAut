# Pipeline

Estágios determinísticos e idempotentes. **Nenhum LLM roda aqui dentro** — ver
seção 2.1 do doc de viabilidade. Rodar duas vezes com a mesma entrada dá o mesmo
resultado e não refaz trabalho.

```
python -m pipeline.s2_tts       fase0/video-02
python -m pipeline.s4_legendas  fase0/video-02
python -m pipeline.s5_render    fase0/video-02
```

| Estágio | Entrada | Saída |
|---|---|---|
| `s2_tts` | `roteiro.md`, bloco `voz` do `plano.json` | `audio/cena_NN.wav`, `duracoes.json` |
| `s4_legendas` | `audio/`, `roteiro.md` | `legendas.pt-BR.srt` |
| `s5_render` | `imagens/`, `audio/`, `plano.json` | `final.mp4` |

`comum.py` tem a infraestrutura: wrapper de ffmpeg que aborta no erro, `ffprobe`,
escape de path para o concat demuxer, e o par `atualizado()`/`marcar()` que dá a
idempotência (grava hash das entradas ao lado da saída).

## O que NÃO existe aqui, de propósito

`s1_roteiro.py` (roteiro por LLM) e `s6_upload.py` (publicação). O CLAUDE.md os
proíbe antes de 2–3 vídeos manuais publicados. O risco do projeto não é técnico —
é construir uma fábrica eficiente para um produto não validado.

`s3_imagens.py` ainda não existe porque depende do Draw Things instalado.

## Decisões travadas nestes scripts

- **O áudio manda no corte.** A duração de cada cena vem do `.wav` dela, não do
  plano. `plano.json` traz alvos; o render usa o real.
- **Um clipe por cena, `concat -c copy` no fim.** Sem reencode na montagem.
  Exige GOP fechado e alinhado (`-g 48 -keyint_min 48 -sc_threshold 0` a 24 fps).
- **`-t` é opção de saída.** Antes do `-i` o comando gera milhões de frames e
  nunca termina. Já custou 8 min de render travado uma vez.
- **`scale=...:flags=neighbor`.** Upscale de pixel art tem que ser nearest e em
  escala inteira (640×360 ×3 = 1920×1080). Qualquer interpolação borra a grade.
- **Imagem parada.** Ken Burns interpola subpixel e destrói pixel art. Movimento
  correto exigiria passo inteiro na grade da fonte; fica para depois.
- **Legenda soft.** `s4` gera `.srt` para `captions.insert`. Nunca queimar.
- **Mix a −18 LUFS**, abaixo do alvo do YouTube, com ducking sidechain do ambiente
  pela narração.
