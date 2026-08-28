---
projeto: Canal de Sono Automatizado
assunto: transição para a máquina com GPU
data: 2026-08-27
status: executado em 27/08/2026 — workstation Windows, RTX 3060 8GB (não a Linux/macOS que este doc presumia; ver SETUP.md para as adaptações de Windows)
---

# Transição para a workstation

Máquina de origem: **MacBook Pro M2, 8 GB RAM, 8 CPUs, sem GPU CUDA.**

O pipeline foi escrito para que trocar de máquina seja **trocar de perfil**, não
reescrever estágio. Tudo que depende de hardware está em `pipeline/perfil.py`.

## O que levar

```
repositório  (git clone)              — código, docs, roteiro, plano
sons/                88 MB, NÃO versionado — ver docs/biblioteca-sons.md
fase0/video-02/audio/   70 MB, NÃO versionado — regenerável com s2_tts
fase0/video-02/imagens/  NÃO versionado — hoje só placeholders
```

Só `sons/` é insubstituível: são downloads externos. O resto o pipeline refaz.

## Checklist

**1. Ambiente base**

```bash
git clone https://github.com/Samuelvieria/VideosAut.git && cd VideosAut
python3.12 -m venv .venv && source .venv/bin/activate
pip install kokoro soundfile numpy faster-whisper pyyaml
# ffmpeg com librubberband e libfreetype (drawtext):
brew install espeak-ng ffmpeg        # macOS
# apt install espeak-ng ffmpeg       # Linux
```

**2. Confirmar que o perfil mudou** — este é o teste que revela se a GPU foi mesmo
aproveitada:

```bash
python -m pipeline.perfil
# esperado: perfil 'workstation': whisper=large-v3/cuda/float16, x264=slow, jobs=6
```

Se disser `m2-8gb` ou `cpu-forte`, **o CUDA não está visível**. Causa quase certa:
o `faster-whisper` usa CTranslate2, não torch, e o wheel padrão do PyPI é CPU.
Instalar a variante com CUDA. Sem isso o whisper roda a 3,4× realtime (~87 min por
vídeo) sem avisar que era para ser melhor.

**3. Regenerar e conferir**

```bash
python -m pipeline.s2_tts      fase0/video-02
python -m pipeline.s5_render   fase0/video-02 --placeholder
python -m pipeline.s4_legendas fase0/video-02
```

O `s5_render` é idempotente: rodar duas vezes com a mesma entrada leva segundos.
Se refizer tudo na segunda vez, a idempotência quebrou.

**4. Geração de imagem** — ver [imagens-provedores.md](imagens-provedores.md).
Recomendação: **Z-Image-Turbo auto-hospedado** (Apache 2.0, custo zero com GPU).
Substitui o Draw Things + SD 1.5, que era imposição dos 8 GB.

## Ganho esperado, medido na máquina antiga

| Estágio | M2 8 GB | Gargalo? |
|---|---|---|
| `s2_tts` (25,4 min de fala) | ~12 min | não |
| `s5_render` (30 min de vídeo) | 8 min; 2,7 s no rerun | não |
| `s4_legendas` (large-v3, CPU) | **~87 min** (3,44× realtime) | **sim** |
| Geração de imagem | inviável local | **sim** |

**A workstation compra duas coisas: os 87 min de legenda e a geração de imagem
local.** O resto já roda bem. Se a migração demorar, `PERFIL=teste` usa o modelo
`small` e corta a legenda para ~17 min — como o texto exibido vem sempre do roteiro
e só o *timing* do whisper sobrevive, a perda é pequena.

## O que NÃO mudar na máquina nova

**Resolução de geração continua 640×360.** Decisão estética, não limitação de
hardware — pixel art é upscalado com `flags=neighbor` em escala inteira ×3. Gerar em
1080p nativo produz pseudo-pixel-art com grade inconsistente. Máquina melhor não é
motivo para mexer.

**A duração continua vindo do áudio**, não do plano.

**`s1_roteiro.py` e `s6_upload.py` continuam proibidos** até 2–3 vídeos publicados.
Mais hardware não valida produto.

## Pendências abertas

- Camada de som gravado sobre a base sintética — implementada em 27/08/2026, ver
  `docs/biblioteca-sons.md`. Ainda falta `stereogenicstudio-beach-02` (11 dos 12
  arquivos foram recuperados), mas não bloqueia a regra atual (usa outros dois).
- Decisão de `speed` da voz pendente — ver `fase0/video-02/teste/`

## Migração real — o que o doc acima não previu

A máquina nova saiu Windows, não Linux/macOS. `SETUP.md` tem a versão completa;
os pontos que valem registro aqui:

- **Sem `winget`/`choco`/`scoop`** nesta máquina — todo binário (Python, ffmpeg)
  foi baixado e extraído manualmente. `python -m pipeline.perfil` sozinho não
  garante GPU de verdade: ele só detecta o driver, não o runtime CUDA. Faltava
  `nvidia-cublas-cu12`/`nvidia-cudnn-cu12` via pip + PATH — ver SETUP.md item 5.
- `pipeline/s2_tts.py` ganhou o wiring do `espeakng-loader` (commit local, a
  aplicar) porque a suposição antiga — espeak-ng resolvido pelo sistema — só
  valia no Mac com brew.
- **Ganho medido bateu com a previsão**: `s4_legendas` (large-v3, 30 min de
  áudio) caiu de ~87 min (CPU, M2) para **6 min** (RTX 3060, cuBLAS/cuDNN via
  pip). `s3_imagens` (Z-Image-Turbo via fal.ai) rodou em ~80s para as 20 cenas.
- Primeiro vídeo completo do pipeline nesta máquina: `fase0/video-02/final.mp4`
  (30 min, 442 MB) + `legendas.pt-BR.srt` (315 legendas), gerado em 27/08/2026.
