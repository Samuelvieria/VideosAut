---
document_type: technical_pipeline
title: Pipeline de Mixagem e Análise Espectral de Áudio Ambiente
stack:
  - ffmpeg
  - numpy
  - scipy
  - matplotlib
domain:
  - audio_processing
  - dsp
  - loudness_metering
status: validado_em_bancada
validation_date: 2026-09-05
tags:
  - ffmpeg
  - loudnorm
  - ebur128
  - fft
  - espectrograma
  - lufs
  - field-recording
version: 1.0
---

# Pipeline de Mixagem e Análise Espectral de Áudio Ambiente

## 1. Limitação de Base (fato, não hipótese)

O modelo **não possui modalidade de áudio**. Não escuta arquivos. A documentação
oficial confirma que todos os modelos atuais suportam entrada de texto e imagem,
saída de texto, multilíngue, visão e uso de ferramentas — áudio não consta.

- https://platform.claude.com/docs/en/about-claude/models/overview
- Issue oficial no SDK confirmando a ausência: https://github.com/anthropics/anthropic-sdk-python/issues/1198

O modo de voz / ditado do app mobile **não é exceção**: roda STT antes da mensagem
chegar ao modelo. O modelo lê texto transcrito, nunca a forma de onda.

Nenhuma skill contorna isso. Skills são instruções + scripts; não adicionam
percepção sensorial.

### Divisão de responsabilidade

| Camada | Responsável | Método |
|---|---|---|
| Julgamento estético ("ficou bom?") | Humano | Ouvido |
| Processamento (EQ, ganho, fade, mix, loudness) | Máquina | ffmpeg / scipy |
| Verificação objetiva (Hz, LUFS, TP, bandas) | Máquina | FFT + EBU R128 |
| Leitura do espectrograma | Modelo | Modalidade de visão (PNG) |

O espectrograma renderizado como PNG **é** legível pelo modelo, porque visão é
modalidade suportada. É por esse caminho que a análise volta ao diálogo.

---

## 2. Ambiente Verificado

Verificado por execução direta no container, não por suposição.

| Componente | Versão | Status |
|---|---|---|
| numpy | 2.4.4 | OK |
| scipy | 1.17.1 | OK |
| matplotlib | 3.10.8 | OK |
| pandas | 3.0.2 | OK |
| ffmpeg / ffprobe | — | OK (`/usr/bin`) |
| librosa | — | Ausente (instalável via PyPI) |
| soundfile | — | Ausente (instalável via PyPI) |

Filtros ffmpeg confirmados disponíveis: `loudnorm`, `ebur128`, `amix`, `afade`,
`acrossfade`, `highpass`, `lowpass`, `pan`, `adelay`, `atrim`, `compand`,
`mcompand`, `acontrast`, `aresample`.

### Restrição de rede

A allowlist do sandbox cobre apenas PyPI, npm, crates e GitHub. **Hipótese de alta
confiança, não testada:** ASR local (Whisper / faster-whisper) falha aqui, porque
os pesos vêm de `huggingface.co` e `openaipublic.azureedge.net`, ambos fora da
allowlist. A biblioteca instala; o download do modelo trava. Transcrição deve ser
feita fora do ambiente.

---

## 3. Arquitetura do Pipeline

```text
arquivos de entrada (WAV/FLAC/MP3/OGG/AIFF)
        │
        ├─ [-stream_loop -1]   loop infinito por camada, se pedido
        │
        ▼
  filter_complex por camada
        highpass / lowpass  → recorte espectral
        volume              → ganho em dB
        pan                 → posicionamento estéreo
        afade in/out        → envelope
        adelay              → entrada temporal deslocada
        atrim               → corte na duração alvo
        │
        ▼
  amix normalize=0          → soma sem divisão automática
        │
        ▼
  loudnorm PASSE 1          → medição (print_format=json)
        │
        ▼
  loudnorm PASSE 2          → normalização linear com valores medidos
        │
        ├─→ WAV 24-bit / 48 kHz
        └─→ MP3 320 kbps
        │
        ▼
  ebur128 + FFT             → verificação independente
        │
        ▼
  PNG (espectro + espectrograma)
```

---

## 4. Armadilhas Conhecidas

### 4.1 `amix` com `normalize=1` (padrão)

O filtro `amix` divide a soma pelo número de entradas por padrão. Com 3 camadas,
o resultado perde cerca de **9,5 dB** silenciosamente. Nenhum aviso é emitido.

```text
ERRADO : amix=inputs=3
CERTO  : amix=inputs=3:normalize=0
```

Com `normalize=0` o controle de nível passa a ser inteiramente do campo
`gain_db` de cada camada — e a soma pode clipar, o que é intencional: o
`loudnorm` posterior corrige, e o true peak é verificado no final.

### 4.2 `loudnorm` em passe único

Em passe único o filtro opera em modo dinâmico e altera a faixa dinâmica do
material. Para ambiente isso é indesejável. O modo correto é dois passes com
`linear=true`, aplicando ganho estático a partir dos valores medidos.

### 4.3 Divergência entre `loudnorm` e `ebur128`

As duas medições usam gating distinto e **não batem exatamente**. No teste de
bancada o LRA reportado caiu de 3,70 para 1,80 sem que o processamento tocasse na
dinâmica — o ganho era estático. A causa é metodológica, agravada por material
curto: **LRA é pouco confiável abaixo de ~60 s**. Em faixas de vários minutos os
valores convergem.

### 4.4 `dropout_transition`

Por padrão o `amix` aplica uma rampa de ganho quando uma entrada termina. Com
camadas de durações diferentes isso gera oscilação audível de nível. Fixar em
`dropout_transition=0`.

---

## 5. Script de Mixagem

```python
#!/usr/bin/env python3
"""
Mixador de camadas ambientes.
Gera filter_complex do ffmpeg a partir de uma config declarativa.
Loudnorm em dois passes (medicao real -> normalizacao linear).
"""
import json, subprocess, sys

SR = 48000

def run(cmd, capture=True):
    return subprocess.run(cmd, capture_output=capture, text=True)

def build_filtergraph(layers, dur):
    parts, labels = [], []
    for i, L in enumerate(layers):
        ch = []
        if L.get("hp"):    ch.append(f"highpass=f={L['hp']}:poles=2")
        if L.get("lp"):    ch.append(f"lowpass=f={L['lp']}:poles=2")
        ch.append(f"volume={L.get('gain_db',0)}dB")
        if L.get("pan") is not None:            # -1 esq .. +1 dir
            p = float(L["pan"])
            gl = (1-p)/2 + 0.5*(1-abs(p))
            gr = (1+p)/2 + 0.5*(1-abs(p))
            ch.append(f"pan=stereo|c0={gl:.4f}*c0|c1={gr:.4f}*c1")
        fi, fo = L.get("fade_in", 0), L.get("fade_out", 0)
        if fi: ch.append(f"afade=t=in:st=0:d={fi}:curve=tri")
        if fo: ch.append(f"afade=t=out:st={dur-fo}:d={fo}:curve=tri")
        if L.get("delay"):
            ms = int(L["delay"]*1000)
            ch.append(f"adelay={ms}|{ms}")
        ch.append(f"atrim=0:{dur}")
        parts.append(f"[{i}:a]" + ",".join(ch) + f"[a{i}]")
        labels.append(f"[a{i}]")
    parts.append("".join(labels) +
                 f"amix=inputs={len(layers)}:normalize=0:dropout_transition=0[mix]")
    return ";".join(parts)

def inputs_args(layers):
    a = []
    for L in layers:
        if L.get("loop"): a += ["-stream_loop", "-1"]
        a += ["-i", L["file"]]
    return a

def measure(path):
    """ffmpeg ebur128 -> LUFS integrado, LRA, true peak"""
    r = run(["ffmpeg","-hide_banner","-nostats","-i",path,
             "-af","ebur128=peak=true","-f","null","-"])
    res = {}
    for line in r.stderr.splitlines():
        s = line.strip()
        for k, tag in [("I:","lufs"), ("LRA:","lra"), ("Peak:","tp")]:
            if s.startswith(k):
                try: res[tag] = float(s.split()[1])
                except (ValueError, IndexError): pass
    return res

def mix(cfg):
    layers, dur = cfg["layers"], cfg["duration"]
    fg = build_filtergraph(layers, dur)
    tmp = "/tmp/_mix_raw.wav"

    cmd = ["ffmpeg","-y","-hide_banner","-nostats"] + inputs_args(layers) + \
          ["-filter_complex", fg, "-map","[mix]",
           "-ar",str(SR),"-ac","2","-c:a","pcm_f32le", tmp]
    r = run(cmd)
    if r.returncode:
        print(r.stderr[-3000:]); sys.exit(1)

    tgt_i   = cfg.get("target_lufs", -23)
    tgt_tp  = cfg.get("target_tp", -1.5)
    tgt_lra = cfg.get("target_lra", 11)

    ln = f"loudnorm=I={tgt_i}:TP={tgt_tp}:LRA={tgt_lra}:print_format=json"
    r = run(["ffmpeg","-hide_banner","-nostats","-i",tmp,"-af",ln,"-f","null","-"])
    blob = r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}")+1]
    m = json.loads(blob)

    ln2 = (f"loudnorm=I={tgt_i}:TP={tgt_tp}:LRA={tgt_lra}:"
           f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
           f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
           f"offset={m['target_offset']}:linear=true:print_format=summary")
    wav = cfg["out_wav"]
    run(["ffmpeg","-y","-hide_banner","-nostats","-i",tmp,"-af",ln2,
         "-ar",str(SR),"-c:a","pcm_s24le", wav])
    if cfg.get("out_mp3"):
        run(["ffmpeg","-y","-hide_banner","-nostats","-i",wav,
             "-c:a","libmp3lame","-b:a","320k", cfg["out_mp3"]])
    return m, measure(wav)

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    pre, post = mix(cfg)
    print("ANTES :", pre["input_i"], "LUFS | TP", pre["input_tp"],
          "dBTP | LRA", pre["input_lra"])
    print("DEPOIS:", post)
```

---

## 6. Esquema de Configuração

```json
{
  "duration": 20,
  "target_lufs": -20,
  "target_tp": -1.5,
  "target_lra": 11,
  "out_wav": "/mnt/user-data/outputs/mix.wav",
  "out_mp3": "/mnt/user-data/outputs/mix.mp3",
  "layers": [
    {
      "file": "chuva.wav",
      "gain_db": -6,
      "hp": 300,
      "lp": 2000,
      "pan": -0.4,
      "fade_in": 3,
      "fade_out": 4,
      "delay": 0,
      "loop": true
    }
  ]
}
```

### Campos

| Campo | Tipo | Unidade | Descrição |
|---|---|---|---|
| `duration` | número | s | Duração final da mixagem |
| `target_lufs` | número | LUFS | Loudness integrado alvo |
| `target_tp` | número | dBTP | Teto de true peak |
| `target_lra` | número | LU | Faixa de loudness alvo |
| `file` | string | — | Caminho do arquivo da camada |
| `gain_db` | número | dB | Ganho da camada |
| `hp` | número | Hz | Passa-alta, 2 polos |
| `lp` | número | Hz | Passa-baixa, 2 polos |
| `pan` | número | −1 a +1 | −1 esquerda, 0 centro, +1 direita |
| `fade_in` | número | s | Rampa de entrada, curva triangular |
| `fade_out` | número | s | Rampa de saída, a partir de `duration − fade_out` |
| `delay` | número | s | Deslocamento de entrada da camada |
| `loop` | bool | — | Repete a camada até preencher `duration` |

### Alvos de loudness por destino

| Destino | LUFS integrado | True peak |
|---|---|---|
| Broadcast EBU R128 | −23 | −1,0 dBTP |
| Spotify / Amazon | −14 | −1,0 dBTP |
| Apple Music | −16 | −1,0 dBTP |
| YouTube | −14 | −1,0 dBTP |
| Cinema / instalação | −23 a −27 | −2,0 dBTP |

---

## 7. Script de Análise Espectral

```python
import numpy as np, subprocess
from scipy import signal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 48000
raw = subprocess.run(
    ["ffmpeg","-v","quiet","-i","mix.wav","-f","f32le","-ac","2","-ar",str(SR),"-"],
    capture_output=True).stdout
x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
m = x.mean(1)

f, P = signal.welch(m, SR, nperseg=16384)

fig, ax = plt.subplots(2, 1, figsize=(9, 7))
ax[0].semilogx(f[1:], 10*np.log10(P[1:] + 1e-14), lw=.8)
ax[0].set_xlim(20, 20000); ax[0].grid(which="both", alpha=.3)
ax[0].set_xlabel("Hz"); ax[0].set_ylabel("dB")
ax[0].set_title("Espectro medio (Welch)")

f2, t2, S = signal.spectrogram(m, SR, nperseg=4096, noverlap=3072)
ax[1].pcolormesh(t2, f2, 10*np.log10(S + 1e-14), shading="gouraud", cmap="magma")
ax[1].set_yscale("symlog", linthresh=100); ax[1].set_ylim(20, 20000)
ax[1].set_xlabel("s"); ax[1].set_ylabel("Hz")
ax[1].set_title("Espectrograma")
plt.tight_layout(); plt.savefig("analise.png", dpi=100)

# distribuicao de energia por banda de oitava
bands = [(31,63),(63,125),(125,250),(250,500),(500,1000),
         (1000,2000),(2000,4000),(4000,8000),(8000,16000)]
tot = np.trapezoid(P, f)
for lo, hi in bands:
    k = (f >= lo) & (f < hi)
    print(f"{lo:5d}-{hi:<6d} | {np.trapezoid(P[k], f[k])/tot*100:6.2f}%")

print("correlacao estereo:", np.corrcoef(x[:,0], x[:,1])[0,1])
```

### Interpretação da correlação estéreo

| Valor | Significado |
|---|---|
| ≈ 1,0 | Mono efetivo, sem imagem estéreo |
| 0,3 a 0,7 | Imagem ampla e compatível com soma mono |
| ≈ 0,0 | Descorrelacionado, máxima largura |
| < 0 | Fase invertida, **cancela ao somar em mono** |

---

## 8. Validação de Bancada

Executado em 2026-09-05 com três camadas sintéticas de 20 s:

| Camada | Sinal | Processamento |
|---|---|---|
| L1 "vento" | Ruído marrom (cumsum de ruído branco) | −6 dB, LP 2 kHz, pan −0,4 |
| L2 "chuva" | Ruído branco com envelope senoidal 0,3 Hz | −10 dB, HP 800 Hz, pan +0,3 |
| L3 "drone" | Senoides 55 / 110 / 165 Hz | −14 dB, LP 400 Hz, delay 2 s |

### Loudness

| Métrica | Antes | Depois | Alvo |
|---|---|---|---|
| Loudness integrado | −21,38 LUFS | −19,70 LUFS | −20 LUFS |
| True peak | −5,17 dBTP | −3,80 dBTP | −1,50 dBTP |
| LRA | 3,70 LU | 1,80 LU | — |

Erro de 0,3 dB no alvo de loudness, dentro do normal para remedição independente.
Corrigível com um terceiro passe se houver exigência de precisão maior.

### Distribuição de energia por banda

| Banda (Hz) | Energia |
|---|---|
| 31 – 63 | 28,97 % |
| 63 – 125 | 7,31 % |
| 125 – 250 | 1,66 % |
| 250 – 500 | 0,05 % |
| 500 – 1 k | 0,53 % |
| 1 k – 2 k | 2,25 % |
| 2 k – 4 k | 4,99 % |
| 4 k – 8 k | 10,09 % |
| 8 k – 16 k | 20,10 % |

Correlação estéreo: 0,952.

A distribuição confirma a configuração: concentração em 31–63 Hz do drone,
vale em 250–500 Hz entre o corte LP do drone e o corte HP da chuva, e subida
acima de 4 kHz da camada de chuva. O espectrograma mostra os picos em
55 / 110 / 165 Hz e a entrada atrasada do drone por volta de 2,5 s.

**Ressalva:** validação feita com sinal sintético. Material real de campo tem
ruído de fundo, DC offset e conteúdo transiente que podem exigir ajuste de
`nperseg` e de janela de análise.

---

## 9. Formatos Aceitos na Entrada

WAV, FLAC, MP3, OGG, AIFF, M4A — qualquer coisa que o ffmpeg decodifique.

**Incerteza não resolvida:** não foi verificado se o uploader do claude.ai aceita
extensões de áudio diretamente. Se recusar, ZIP contorna.

---

## 10. Referências

- ffmpeg, filtros de áudio: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters
- ffmpeg `loudnorm`: https://ffmpeg.org/ffmpeg-filters.html#loudnorm
- ffmpeg `ebur128`: https://ffmpeg.org/ffmpeg-filters.html#ebur128-1
- EBU R128, recomendação de loudness: https://tech.ebu.ch/publications/r128
- ITU-R BS.1770, algoritmo de medição: https://www.itu.int/rec/R-REC-BS.1770
- scipy.signal: https://docs.scipy.org/doc/scipy/reference/signal.html
- numpy: https://numpy.org/doc/
- Modalidades suportadas pelo modelo: https://platform.claude.com/docs/en/about-claude/models/overview
