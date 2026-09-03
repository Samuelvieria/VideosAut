#!/usr/bin/env python3
"""s5 — monta o vídeo final a partir de imagens + narração por cena + ambiente.

    python -m pipeline.s5_render fase0/video-02 [--placeholder] [--forcar]

Arquitetura (medida em 26/08/2026, ver CLAUDE.md):
  - cada cena vira um clipe independente com fade para preto e GOP alinhado;
  - a montagem final é `concat -c copy` — instantânea, sem reencode;
  - a duração de cada clipe vem do ÁUDIO daquela cena, não do plano.

Movimento de imagem (27/08/2026): as cenas narradas deslizam devagar (pan
horizontal), a cauda sem narração fica parada. O estilo é pixel art — zoom/pan
contínuo do jeito ingênuo (`zoompan`/escala variável) reamostra em subpixel e
destrói a grade de pixels, que é o estilo inteiro. A saída: `s3_imagens` gera
768×432 (640×360 de densidade real + 128×72 de margem); aqui se corta uma
janela de 640×360 — sempre esse tamanho, parada ou deslizando pela margem —
por PIXEL INTEIRO (`crop` nunca reamostra), escalando por um fator inteiro
exato ×3 até 1920×1080. Ver `clipe_cena` e as constantes `PAN_*`.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import (FFMPEG, RAIZ, atualizado, carregar_plano, duracao, erro,
                            ffmpeg, lista_concat, log, marcar, projeto)
from pipeline.perfil import perfil
from pipeline import ambiente as amb

FPS = 24
LARG, ALT = 1920, 1080
GOP = FPS * 2
PAUSA_ENTRE_CENAS = 2.0   # respiro entre cenas; também dá tempo do fade acontecer
FADE = 1.5

# Movimento por passo INTEIRO na grade da fonte. A escala tem que ser inteira
# ou o pixel art borra — essa é a restrição que manda em todos os números aqui.
#
# MEDIDO 02/09/2026: a fal.ai não entrega dimensão abaixo de 512, então 640×360
# e 768×432 nunca existiram — vinham 640×512 e 768×512, fora de 16:9. O código
# anterior assumia 768×432 e cortava 640×360 em y=36, descartando em silêncio
# os 116px de baixo de toda cena.
#
# Com fonte 1024×576 (nativo do modelo) sobram duas janelas de escala inteira:
#   640×360 ×3 -> mostra só 62% do quadro; corta composição demais
#   960×540 ×2 -> mostra 94%, sobra margem 64×36 pro pan   <- escolhida
SRC_L, SRC_A = 1280, 720          # o que o s3_imagens gera
PAN_ESCALA = 2                    # nearest ×2 — pixel art exige escala inteira
PAN_MARGEM_X = SRC_L * PAN_ESCALA - LARG      # 640 px de saída
PAN_MARGEM_Y = SRC_A * PAN_ESCALA - ALT       # 360 px de saída
# VELOCIDADE constante, não percurso constante. MEDIDO 03/09/2026: fixando o
# percurso em 640px e deixando o tempo variar, cena de 50s andava a 12,8 px/s e
# cena de 110s a 5,8 px/s — a maioria das cenas é longa, então a maioria ficou
# no pior caso (0,208s entre passos contra 0,042s da cena curta).
#
# Onda triangular: velocidade constante em cada trecho, com reversão nas pontas.
# Triângulo e não seno justamente porque seno tem derivada zero nos extremos, que
# foi a causa original do travado.
PAN_VEL_X = 12.0    # px de saída por segundo — ~1 passo a cada 2 frames a 24fps
PAN_VEL_Y = 6.75    # proporcional à margem (360/640), para a diagonal ficar reta


def _cenas_narradas(plano: dict) -> list[dict]:
    return [c for c in plano["cenas"] if c["papel"] != "cauda-ambiente"]


def _cena_cauda(plano: dict) -> dict | None:
    c = [c for c in plano["cenas"] if c["papel"] == "cauda-ambiente"]
    return c[0] if c else None


def placeholders(proj: Path, plano: dict) -> None:
    """Imagens sólidas de teste, para exercitar o render antes do Draw Things."""
    d = proj / "imagens"; d.mkdir(exist_ok=True)
    paleta = ["#0d1117", "#2b3a4a", "#4a5a6a", "#e8a54b", "#c8632a"]
    for c in plano["cenas"]:
        alvo = d / f"cena_{c['n']:02d}.png"
        if alvo.exists():
            continue
        cor = paleta[c["n"] % len(paleta)]
        ffmpeg(["-f", "lavfi", "-i", f"color=c={cor}:s={SRC_L}x{SRC_A}", "-frames:v", "1",
                str(alvo)], f"placeholder cena {c['n']}")
    log(f"placeholders em {d}")


def trilha_narracao(proj: Path, cenas: list[dict], forcar: bool) -> tuple[Path, float]:
    """Concatena as narrações com PAUSA_ENTRE_CENAS de silêncio entre elas."""
    wavs = [proj / "audio" / f"cena_{c['n']:02d}.wav" for c in cenas]
    faltando = [w.name for w in wavs if not w.exists()]
    if faltando:
        erro(f"faltam áudios de cena: {', '.join(faltando)}\nRode s2_tts antes.")

    saida = proj / "build" / "narracao_completa.wav"
    saida.parent.mkdir(exist_ok=True)
    cfg = f"pausa={PAUSA_ENTRE_CENAS}"
    if not forcar and atualizado(saida, wavs, cfg):
        log("narração concatenada: já atualizada")
        return saida, duracao(saida)

    entradas: list[str] = []
    filtros: list[str] = []
    for i, w in enumerate(wavs):
        entradas += ["-i", str(w)]
        # apad no fim de cada cena = o respiro entre imagens
        filtros.append(f"[{i}:a]aresample=48000,apad=pad_dur={PAUSA_ENTRE_CENAS}[a{i}]")
    cadeia = "".join(f"[a{i}]" for i in range(len(wavs)))
    filtros.append(f"{cadeia}concat=n={len(wavs)}:v=0:a=1[out]")

    ffmpeg([*entradas, "-filter_complex", ";".join(filtros),
            "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", str(saida)],
           "concat da narração")
    marcar(saida, wavs, cfg)
    d = duracao(saida)
    log(f"narração concatenada: {d/60:.1f} min")
    return saida, d


CROSSFADE = 3.0   # transição entre ambientes de cena; cai junto com o fade do vídeo

# Camada gravada sobre a base sintética (docs/biblioteca-sons.md, pendência
# registrada em 26/08/2026, implementada em 27/08/2026 depois de ouvir o
# video-02: síntese pura demais soa a ruído filtrado, não a chuva/mar de
# verdade). Regra por CENA a partir do que o plano.json já tem (mar/chuva),
# sem precisar de campo novo: chuva forte usa o único trovão "usável em sono"
# do lote (loswin23-thunderstorm-2 — os outros têm estouro seco demais); mar
# sem chuva forte usa a cama mais longa e equilibrada (enternalrainsounds,
# 900s, cobre a cena inteira sem repetir o início toda vez). Nunca as duas
# juntas — vira camada, não confusão.
SONS = RAIZ / "sons"
_TEMPESTADE = SONS / "loswin23-thunderstorm-2-516370.mp3"
_MAR_CAMA = SONS / "enternalrainsounds-light-rain-with-gentle-ocean-waves-mix-420329.mp3"


def _escolher_gravado(cfg: dict) -> tuple[Path, float] | None:
    chuva, mar = cfg.get("chuva", 0), cfg.get("mar", 0)
    if chuva >= 0.5 and _TEMPESTADE.is_file():
        return _TEMPESTADE, 0.35 * chuva
    if mar >= 0.3 and not cfg.get("abafado") and _MAR_CAMA.is_file():
        return _MAR_CAMA, 0.25 * mar
    return None


def _ambiente_cena(dest: Path, dur: float, cfg: dict, n: int = 0) -> None:
    """Gera o ambiente de UMA cena, conforme o perfil dela no plano."""
    nos, camadas = [], {"L": [], "R": []}
    for canal in ("L", "R"):
        if cfg.get("mar", 0) > 0:
            nos += amb.mar(dur, canal, cfg["mar"]);      camadas[canal].append(f"[mar{canal}]")
        if cfg.get("chuva", 0) > 0:
            nos += amb.chuva(dur, canal, cfg["chuva"], cfg.get("abafado", False))
            camadas[canal].append(f"[chuva{canal}]")
        if cfg.get("fogo", 0) > 0:
            nos += amb.fogo(dur, canal, cfg["fogo"]);    camadas[canal].append(f"[fogo{canal}]")
        if cfg.get("vento", 0) > 0:
            nos += amb.vento(dur, canal, cfg["vento"]);  camadas[canal].append(f"[vento{canal}]")

    if not camadas["L"]:   # cena sem ambiente: silêncio, não erro
        ffmpeg(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={dur}",
                "-c:a", "pcm_s16le", str(dest)], "ambiente vazio")
        return

    entrada_args = []
    gravado = _escolher_gravado(cfg)
    if gravado:
        arquivo, ganho = gravado
        # deslocamento por cena para não começar sempre no mesmo trecho do
        # arquivo (é a repetição que dá pra "reconhecer" ouvindo várias cenas)
        offset = (n * 137) % 400
        entrada_args = ["-stream_loop", "-1", "-ss", str(offset), "-i", str(arquivo)]

    for canal in ("L", "R"):
        c = camadas[canal]
        if len(c) > 1:
            nos.append(f"{''.join(c)}amix=inputs={len(c)}:duration=longest:normalize=0[mix{canal}]")
        else:
            nos.append(f"{c[0]}anull[mix{canal}]")

    f = min(CROSSFADE, dur / 3)
    if gravado:
        _, ganho = gravado
        nos.append(f"[0:a]atrim=0:{dur},asetpts=PTS-STARTPTS,"
                   f"aformat=channel_layouts=stereo,volume={ganho}[grav]")
        nos.append(f"[mixL][mixR]join=inputs=2:channel_layout=stereo[sint]")
        nos.append(f"[sint][grav]amix=inputs=2:duration=first:normalize=0,"
                   f"afade=t=in:st=0:d={f:.2f},afade=t=out:st={dur-f:.2f}:d={f:.2f},"
                   f"loudnorm=I=-24:TP=-3.0:LRA=9[out]")
    else:
        nos.append(f"[mixL][mixR]join=inputs=2:channel_layout=stereo,"
                   f"afade=t=in:st=0:d={f:.2f},afade=t=out:st={dur-f:.2f}:d={f:.2f},"
                   f"loudnorm=I=-24:TP=-3.0:LRA=9[out]")
    ffmpeg([*entrada_args, "-filter_complex", ";".join(nos), "-map", "[out]",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(dest)], f"ambiente {dest.name}")


def trilha_ambiente(proj: Path, plano: dict, duracoes: dict, forcar: bool) -> Path:
    """Ambiente POR CENA, concatenado — não uma trilha única.

    Segue o lugar e o momento do roteiro: tempestade no cais, interior da
    estalagem com lareira, mar aberto, calmaria. A troca acontece no mesmo
    instante do fade para preto do vídeo, então lê como corte intencional em vez
    de emenda de áudio.
    """
    saida = proj / "build" / "ambiente.wav"
    saida.parent.mkdir(exist_ok=True)
    perfis = {c["n"]: c.get("ambiente", {}) for c in plano["cenas"]}
    cfg = json.dumps({str(k): [perfis.get(k), round(v, 1)] for k, v in sorted(duracoes.items())},
                     sort_keys=True) + ";v2-camada-gravada"
    if not forcar and atualizado(saida, [], cfg):
        log("ambiente: já atualizado")
        return saida

    d = proj / "build" / "amb_cenas"; d.mkdir(parents=True, exist_ok=True)
    partes = []
    for n in sorted(duracoes):
        alvo = d / f"amb_{n:02d}.wav"
        _ambiente_cena(alvo, duracoes[n], perfis.get(n, {}), n)
        partes.append(alvo)
        p = perfis.get(n, {})
        log(f"  cena {n:02d}  mar={p.get('mar',0):.2f} chuva={p.get('chuva',0):.2f} "
            f"fogo={p.get('fogo',0):.2f}  {p.get('_','')[:38]}")

    lista = lista_concat(proj / "build" / "amb_concat.txt", partes)
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lista),
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(saida)], "concat do ambiente")
    marcar(saida, [], cfg)
    log(f"ambiente por cena: {duracao(saida)/60:.1f} min")
    return saida


# Padrão do bloco `mixagem` do plano.json — usado quando o vídeo não tem essa
# seção (compatível com vídeos antigos) e como valor inicial no mixer do
# estudio/. `reverb` é um multiplicador (0-1) sobre REVERB_DECAY_BASE; os
# outros valores vão direto pros filtros de ffmpeg abaixo.
#
# Recalibrado em 28/08/2026 a partir de pesquisa de mercado pra loudness de
# vídeo de sono (sem norma oficial ITU/EBU/AES pra esse nicho especificamente
# — números vêm de WCAG G56, prática de podcast/audiolivro e documentação do
# próprio YouTube; ver .claude/skills/qualidade-producao-video/SKILL.md):
#   - ambiente_ganho subiu de 0.1 pra 1.0: medido (isolando cada stem, ver
#     SKILL.md) que 0.1 dava gap de +25dB da voz (quase mudo) e mesmo 0.42
#     (calculado a partir do arquivo bruto sem processar) ainda dava ~21dB —
#     os cortes de EQ novos (highpass, dip 1-4kHz, lowpass) tiram mais
#     energia do que o cálculo ingênuo previa. 1.0 mede ~13,6dB de gap,
#     dentro do alvo de 12-15dB pra ambiente de ruído banda-larga (WCAG
#     recomenda ≥20dB pra música, mas ruído sem melodia não compete com a
#     fala do mesmo jeito).
#   - duck_ratio caiu de 4 pra 2 e duck_release subiu de 450ms pra 2000ms:
#     ducking forte + rápido "bombeia" (fica óbvio o ambiente subindo/caindo);
#     pra sono o alvo é reduzir só 4-6dB, de forma lenta o bastante pra não
#     ser percebido como evento.
MIXAGEM_PADRAO = {
    "voz_ganho": 1.0,
    "voz_reverb": 0.5,
    "voz_deesser": 0.4,
    "ambiente_ganho": 1.0,
    "ambiente_reverb": 0.7,
    "ambiente_lowpass_hz": 5500,
    "duck_threshold": 0.05,
    "duck_ratio": 2,
    "duck_attack_ms": 200,
    "duck_release_ms": 2000,
    # A cauda (ambiente sem voz) precisa SUBIR quando a narração acaba. Durante
    # a narração o loudnorm normaliza voz+ambiente somados, e a voz domina a
    # soma; quando ela sai, sobra o ambiente no nível em que sempre esteve.
    # MEDIDO 03/09/2026 no vídeo 02: narração a -14,3 LUFS e cauda a -26,4 —
    # 12,1 dB de queda. Quem ajusta o volume pela voz perde a cauda inteira, e
    # a cauda existe justamente para cobrir a transição do sono.
    "cauda_ganho": 2.6,        # ~+8,3 dB, deixa a cauda ~4 dB abaixo da narração
    "cauda_rampa_s": 45.0,     # subida lenta; degrau seco seria audível
}
REVERB_DELAYS_MS = [40, 70, 110, 160]
REVERB_DECAY_BASE = [0.5, 0.4, 0.28, 0.2]   # ×ambiente_reverb=1.0 = reverb máximo
VOZ_REVERB_DELAYS_MS = [23, 37]             # sala pequena — bem mais curto que o do ambiente
VOZ_REVERB_DECAY_BASE = [0.20, 0.14]        # ×voz_reverb=1.0 = eco máximo; 0.5 = padrão antigo

# Alvo de masterização final — YouTube normaliza tudo pra -14 LUFS integrado;
# entregar mais baixo (era -18) só faz o espectador subir o volume do
# aparelho, e aí o próximo vídeo/anúncio (normalizado em -14) toca alto
# demais. O "quão suave" certo vem de LRA estreito, não de nível baixo.
#
# TP alvo passado ao loudnorm é -1.5, não -1.0: o teto de segurança real do
# checklist é -1.0 dBTP, mas o loudnorm (mesmo em 2 passos, linear=true)
# overshoot o TP pedido em ~0.1-0.4dB na prática — medido em 28/08/2026 no
# video-02: alvo -1.0 mediu -0.88 (passou do teto). Pedir -1.5 mediu -1.40 de
# verdade, com margem. Ver .claude/skills/qualidade-producao-video/SKILL.md.
MASTER_I, MASTER_TP, MASTER_LRA = -14.0, -1.5, 6.0


def _ganho_ambiente(m: dict, narr_s: float, janela: tuple | None) -> str:
    """Expressão de ganho do ambiente, com rampa de subida ao fim da narração.

    Retorna o ganho constante quando não há cauda. Com cauda, sobe de
    `ambiente_ganho` para `ambiente_ganho * cauda_ganho` ao longo de
    `cauda_rampa_s`, começando quando a voz termina.
    """
    g, r, rampa = m["ambiente_ganho"], m.get("cauda_ganho", 1.0), m.get("cauda_rampa_s", 45.0)
    if r <= 1.0 or narr_s <= 0:
        return f"{g}"
    # no modo janela o tempo do filtro começa em 0, mas corresponde a inicio_s
    t0 = narr_s - (janela[0] if janela else 0.0)
    return f"{g}*(1+{r - 1:.4f}*min(1,max(0,(t-{t0:.2f})/{rampa:.1f})))"


def mixar(proj: Path, narracao: Path, ambiente: Path, total_s: float, forcar: bool,
          mixagem: dict | None = None, janela: tuple[float, float] | None = None) -> Path:
    """Ducking sidechain + masterização a -14 LUFS / -1 dBTP (o alvo real do
    YouTube — ver MASTER_I). Era -18 (deliberadamente abaixo) até 28/08/2026;
    mudou porque entregar mais baixo faz o espectador subir o volume do
    aparelho, e o próximo vídeo/anúncio normalizado em -14 toca alto demais
    — quem deve controlar "quão baixo" é o volume do aparelho do ouvinte,
    não o master. O conforto do formato vem de LRA estreito, não de nível
    baixo. Ver .claude/skills/qualidade-producao-video/SKILL.md.

    A voz fica MONO e centrada de propósito: narração é o foco e tem que vir de
    um ponto só. Quem ganha largura é o ambiente. Voz espalhada no campo estéreo
    soa difusa e atrapalha o adormecer, que é o oposto do que o vídeo existe para
    fazer.

    `mixagem` sobrepõe MIXAGEM_PADRAO — vem do bloco `mixagem` do plano.json,
    editável pelo mixer do estudio/ sem mexer em código (ver estudio/routers/mixer.py).

    `janela=(inicio_s, dur_s)` processa só um TRECHO em vez do vídeo inteiro —
    ouvir um ajuste de mixagem não pode depender de esperar os 30+ min
    completos toda vez. Sai em `build/mix_preview.m4a`, nunca sobrescreve o
    `mix.m4a` real usado no render final.
    """
    m = {**MIXAGEM_PADRAO, **(mixagem or {})}
    narr_s = duracao(narracao)   # narração pura, antes do apad estender
    if janela:
        inicio_s, dur_s = janela
        saida = proj / "build" / "mix_preview.m4a"
        bruto = proj / "build" / "mix_bruto_preview.wav"
        entrada = ["-ss", f"{inicio_s:.2f}", "-i", str(narracao),
                   "-ss", f"{inicio_s:.2f}", "-i", str(ambiente)]
    else:
        dur_s = total_s
        saida = proj / "build" / "mix.m4a"
        bruto = proj / "build" / "mix_bruto.wav"
        entrada = ["-i", str(narracao), "-i", str(ambiente)]

    cfg = (f"total={dur_s:.1f};janela={janela};cena=v12-cauda-rampa;voz=eq+comp+sala+deess;"
           + ";".join(f"{k}={v}" for k, v in sorted(m.items())))
    if not forcar and atualizado(saida, [narracao, ambiente], cfg):
        log("mix: já atualizado")
        return saida

    decays = "|".join(f"{d*m['ambiente_reverb']:.3f}" for d in REVERB_DECAY_BASE)
    delays = "|".join(str(d) for d in REVERB_DELAYS_MS)
    voz_decays = "|".join(f"{d*m['voz_reverb']:.3f}" for d in VOZ_REVERB_DECAY_BASE)
    voz_delays = "|".join(str(d) for d in VOZ_REVERB_DELAYS_MS)

    ffmpeg([*entrada, "-filter_complex",
            # voz mono -> duplicada nos dois canais (centro), estendida com silêncio
            # asplit explícito: a voz é consumida DUAS vezes (sidechain + mix). O
            # ffmpeg tolera reusar o label num grafo só-áudio, mas falha com
            # "matches no streams" se houver vídeo no mesmo filtergraph. Verificado
            # no ffmpeg 9.0.1. asplit funciona nos dois casos.
            # Cadeia de voz. TTS soa robótico por três motivos tratáveis:
            # médio-agudo estridente em 2-4 kHz, dinâmica plana demais, e ausência
            # de qualquer sala — a voz "flutua" fora de um espaço físico. Ganho
            # entra DEPOIS do compressor (só nível, não muda quanto comprime) e
            # ANTES do eco (a cauda de reverb escala junto com o volume).
            f"[0:a]aformat=channel_layouts=mono,"
            f"highpass=f=80,"                       # tira ronco abaixo da voz
            f"equalizer=f=325:t=q:w=1.5:g=-3,"      # corta abafado/mud (250-400Hz)
            f"equalizer=f=3000:t=q:w=1.4:g=-3,"     # corta a aspereza digital
            f"treble=f=9000:g=-2:width_type=o:width=1,"  # shelf alto — reduz "ar"/sibilância residual
            f"deesser=i={m['voz_deesser']}:f=0.6,"  # o "S" estourado é o principal despertador em fone
            f"acompressor=threshold=-18dB:ratio=3:attack=15:release=250:knee=6,"
            f"volume={m['voz_ganho']},"
            f"aecho=0.92:0.85:{voz_delays}:{voz_decays},"  # sala pequena
            # loudnorm da VOZ SOZINHA, não do mix somado — normalizar depois
            # de somar com o ambiente reinflava o volume geral (ambiente
            # incluso) sempre que a soma ficava baixa demais, meio que
            # desfazendo o ganho baixo escolhido no mixer. Com a voz num
            # nível fixo e conhecido, ambiente_ganho passa a ser um
            # multiplicador direto de verdade, sem nada compensando depois.
            # Esse loudnorm aqui é só um "leveler" pra manter a voz
            # consistente cena a cena — o alvo de masterização real
            # (MASTER_I/-14 LUFS) entra depois, em 2 passos, no fim de tudo.
            #
            # loudnorm entra DEPOIS do pan=stereo, não antes: medir loudness
            # num sinal ainda mono e só depois duplicar pros dois canais
            # (pan=stereo|c0=c0|c1=c0) sai ~3dB mais alto que o alvo — o
            # BS.1770 soma os dois canais do estéreo "mono duplicado", então
            # o mesmo conteúdo mede mais alto em estéreo que em mono. Medido
            # em 28/08/2026: alvo -18 LUFS, saída real -14.3 LUFS até corrigir
            # a ordem.
            f"apad=whole_dur={dur_s},"
            f"pan=stereo|c0=c0|c1=c0,"
            f"loudnorm=I=-18:TP=-3.0:LRA=5,"
            f"asplit=2[voz_sc][voz_mix];"
            # Ambiente "no fundo": mais baixo que a voz, com pseudo-reverb de
            # sala grande (aecho com várias repetições longas — não tem
            # afreeverb neste build de ffmpeg) e lowpass (som distante perde
            # agudo). Os 4 números vêm do bloco `mixagem` do plano.json.
            f"[1:a]aformat=channel_layouts=stereo,highpass=f=45,"
            f"volume=volume='{_ganho_ambiente(m, narr_s, janela)}':eval=frame,"
            f"aecho=0.8:0.7:{delays}:{decays},"
            # dip espectral 1-4kHz ("sidechain EQ"): abre espaço pra
            # inteligibilidade da voz sem precisar baixar o ambiente inteiro
            # — dá pra manter mais presença no resto do espectro com o
            # mesmo gap percebido.
            f"equalizer=f=2000:t=q:w=1.5:g=-3.5,"
            f"lowpass=f={m['ambiente_lowpass_hz']}[amb];"
            # release era 1800ms fixo — mais longo que as pausas de respiração
            # (300-450ms, ver s2_tts.py), então o ambiente nunca "voltava"
            # durante a narração. Editável no mixer agora. Alvo atual (ver
            # MIXAGEM_PADRAO): reduzir só 4-6dB, devagar — ducking forte e
            # rápido "bombeia" (fica óbvio), o que é o oposto do que sono pede.
            f"[amb][voz_sc]sidechaincompress=threshold={m['duck_threshold']}:"
            f"ratio={m['duck_ratio']}:attack={m['duck_attack_ms']}:"
            f"release={m['duck_release_ms']}[duck];"
            # só limita pico da soma — NÃO normaliza loudness geral aqui, a
            # masterização de verdade (2 passos, ganho linear) vem depois,
            # em cima do arquivo já pronto. Ver _masterizar_2passos().
            f"[duck][voz_mix]amix=inputs=2:duration=longest:normalize=0,"
            f"alimiter=limit=0.98:attack=5:release=50[out]",
            "-map", "[out]", "-t", f"{dur_s}",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(bruto)],
           "mix bruto (pré-masterização)")

    _masterizar_2passos(bruto, saida)
    marcar(saida, [narracao, ambiente], cfg)
    log(f"mix {'preview' if janela else 'estéreo'}: {duracao(saida):.0f}s" if janela
        else f"mix estéreo: {duracao(saida)/60:.1f} min")
    return saida


def _masterizar_2passos(bruto: Path, saida: Path) -> None:
    """loudnorm de 2 passos (`linear=true`) no mix já pronto — ganho FIXO
    (só um offset), preserva a relação voz/ambiente calibrada no resto da
    cadeia. O loudnorm de 1 passo (dinâmico) reage à loudness corrente e
    reinflava o volume geral sempre que a soma ficava baixa — foi esse o bug
    que motivou tirar o loudnorm de dentro do filtro complexo (ver mixar()).
    Alvo: MASTER_I/-14 LUFS, o que o YouTube normaliza — entregar mais baixo
    só faz o espectador subir o volume do aparelho e levar um susto no
    próximo vídeo/anúncio, que toca em -14.
    """
    alvo = f"I={MASTER_I}:TP={MASTER_TP}:LRA={MASTER_LRA}"
    analise = subprocess.run(
        [FFMPEG, "-i", str(bruto), "-af", f"loudnorm={alvo}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    try:
        bruto_json = analise.stderr[analise.stderr.rindex("{"):analise.stderr.rindex("}") + 1]
        stats = json.loads(bruto_json)
    except (ValueError, json.JSONDecodeError):
        erro(f"loudnorm (análise) não devolveu estatísticas válidas:\n{analise.stderr[-800:]}")
    medidos = (f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
               f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}")
    ffmpeg(["-i", str(bruto), "-af", f"loudnorm={alvo}:{medidos}:linear=true",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(saida)],
           "masterização 2 passos")


def _dimensoes_png(caminho: Path) -> tuple[int, int]:
    """Largura e altura direto do cabeçalho PNG, sem decodificar a imagem."""
    import struct
    with open(caminho, "rb") as f:
        cab = f.read(33)
    if cab[:8] != b"\x89PNG\r\n\x1a\n":
        erro(f"{caminho} não é PNG")
    return struct.unpack(">II", cab[16:24])


def _confere_fonte(img: Path) -> None:
    """Aborta se a imagem não tem o tamanho que as constantes de pan assumem.

    Existe porque a ausência desta checagem deixou um bug rodar em silêncio: o
    código assumia fonte 768×432, a fal.ai entregava 768×512, e o crop comia
    116px do rodapé de toda cena sem nenhum aviso. Errar alto é melhor do que
    entregar 30 min de vídeo com a composição cortada.
    """
    w, h = _dimensoes_png(img)
    if (w, h) != (SRC_L, SRC_A):
        erro(f"{img.name} é {w}×{h}, mas o render assume {SRC_L}×{SRC_A}.\n"
             f"  A janela de corte ({PAN_L}×{PAN_A}) e a escala ×{PAN_ESCALA} dependem disso.\n"
             f"  Regere as imagens:  python -m pipeline.s3_imagens {img.parent.parent} --forcar")


def clipe_cena(proj: Path, n: int, dur: float, forcar: bool, preset: str = "medium",
               mover: bool = True) -> Path:
    img = proj / "imagens" / f"cena_{n:02d}.png"
    if not img.exists():
        erro(f"falta {img}. Gere as imagens ou rode com --placeholder.")
    _confere_fonte(img)

    saida = proj / "build" / "clipes" / f"cena_{n:02d}.mp4"
    saida.parent.mkdir(parents=True, exist_ok=True)
    cfg = f"dur={dur:.2f};fps={FPS};fade={FADE};preset={preset};mover={mover};v6-pan-vel-constante"
    if not forcar and atualizado(saida, [img], cfg):
        return saida

    f_out = max(0.0, dur - FADE)

    # MEDIDO 03/09/2026. O vaivém senoidal anterior lia como TRAVADO, e a causa
    # não era o tamanho do passo — era a irregularidade. Sobre uma cena de 100s:
    #
    #   seno, corte no espaço da fonte:  passo de 2px, intervalo 0,04s a 3,21s
    #                                    -> razão max/mediana 12,8x
    #   linear, corte no espaço da saída: passo de 1px, intervalo 0,75s a 0,79s
    #                                    -> razão 1,0x
    #
    # Nos extremos do seno a derivada é zero e a imagem CONGELA por 3 segundos;
    # no meio dispara 25 passos por segundo. O olho lê o contraste, não a média.
    #
    # Duas correções somadas:
    # 1. Escalar ANTES de cortar. Cortando na fonte e escalando depois, cada
    #    passo de 1px da fonte virava 2px na tela. Escalando primeiro, o corte
    #    anda em pixels de SAÍDA e o passo cai pela metade.
    # 2. Linear em vez de seno — velocidade constante, passos regulares.
    #
    # Com fonte 1280×720 a margem é 640×360 de saída: ~12 passos/s em diagonal,
    # contra 1,3/s antes. A 24 fps isso lê como deslize contínuo.
    fase_x, fase_y = [(0, 1), (1, 0), (0, 0), (1, 1)][n % 4]

    def _eixo(margem: int, vel: float, fase: int) -> str:
        """Onda triangular de velocidade constante, entre 0 e `margem`.

        `abs(mod(2t/P+1,2)-1)` desenha o triângulo; P = 2*margem/vel é o tempo de
        ida e volta. Fase 1 começa da outra ponta, para as cenas não deslizarem
        todas no mesmo sentido.
        """
        if not mover or margem <= 0 or vel <= 0:
            return str(margem // 2)
        P = 2 * margem / vel
        desloc = 1 + fase          # fase 0 começa em 0; fase 1 começa na margem
        return f"trunc({margem}*abs(mod(2*t/{P:.2f}+{desloc},2)-1))"

    # scale ANTES do crop: nearest ×2 mantém a grade de pixel art cravada, e o
    # crop que segue nunca reamostra — só escolhe quais pixels aparecem.
    vf = (f"scale={SRC_L * PAN_ESCALA}:{SRC_A * PAN_ESCALA}:flags=neighbor,"
          f"crop={LARG}:{ALT}:x='{_eixo(PAN_MARGEM_X, PAN_VEL_X, fase_x)}':y='{_eixo(PAN_MARGEM_Y, PAN_VEL_Y, fase_y)}',"
          f"format=yuv420p,"
          f"fade=t=in:st=0:d={FADE},fade=t=out:st={f_out:.2f}:d={FADE}")
    ffmpeg(["-loop", "1", "-framerate", str(FPS), "-i", str(img),
            "-vf", vf,
            "-t", f"{dur:.3f}",            # -t é opção de SAÍDA (ver CLAUDE.md)
            "-c:v", "libx264", "-preset", preset, "-crf", "21",
            "-tune", "stillimage",
            "-g", str(GOP), "-keyint_min", str(GOP), "-sc_threshold", "0",
            "-an", str(saida)], f"clipe cena {n}")
    marcar(saida, [img], cfg)
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description="Monta o vídeo final.")
    ap.add_argument("projeto")
    ap.add_argument("--placeholder", action="store_true",
                    help="cria imagens sólidas de teste para as cenas que faltam")
    ap.add_argument("--forcar", action="store_true", help="ignora o cache de idempotência")
    ap.add_argument("--jobs", type=int, default=None,
                    help="clipes em paralelo (padrão: do perfil)")
    ap.add_argument("--so-mix", action="store_true",
                    help="refaz só o mix de áudio (build/mix.m4a) e para — "
                         "pra ouvir um ajuste do mixer sem re-renderizar o vídeo inteiro")
    ap.add_argument("--preview-s", type=float, default=None,
                    help="com --so-mix: processa só N segundos (build/mix_preview.m4a) "
                         "em vez do áudio inteiro — preview quase instantâneo do mixer")
    ap.add_argument("--preview-inicio", type=float, default=0.0,
                    help="com --preview-s: onde começar, em segundos (padrão: 0 = cena 1)")
    a = ap.parse_args()

    hw = perfil()
    log(str(hw))

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    if a.placeholder:
        placeholders(proj, plano)

    narradas = _cenas_narradas(plano)
    cauda = _cena_cauda(plano)

    print(f"\n[1/5] narração")
    narracao, dur_narr = trilha_narracao(proj, narradas, a.forcar)

    # A duração de cada cena narrada é a do seu áudio + a pausa.
    duracoes = {}
    for c in narradas:
        w = proj / "audio" / f"cena_{c['n']:02d}.wav"
        duracoes[c["n"]] = duracao(w) + PAUSA_ENTRE_CENAS

    alvo = float(plano.get("duracao_alvo_s", 1800))
    if cauda:
        resto = alvo - sum(duracoes.values())
        if resto < 30:
            log(f"AVISO: narração ocupou {sum(duracoes.values())/60:.1f} min do alvo de "
                f"{alvo/60:.0f} min; cauda ficaria em {resto:.0f}s. Usando 60s.")
            resto = 60.0
        duracoes[cauda["n"]] = resto
    total = sum(duracoes.values())

    print(f"[2/5] ambiente por cena")
    ambiente = trilha_ambiente(proj, plano, duracoes, a.forcar)

    print(f"[3/5] mix")
    janela = (a.preview_inicio, min(a.preview_s, total - a.preview_inicio)) if a.preview_s else None
    mix = mixar(proj, narracao, ambiente, total, a.forcar, plano.get("mixagem"), janela)

    if a.so_mix:
        log(f"--so-mix: parando aqui — {mix}")
        return

    jobs = a.jobs or hw.jobs
    print(f"[4/5] clipes de cena ({len(duracoes)}, {jobs} em paralelo)")
    pendentes = [c for c in plano["cenas"] if c["n"] in duracoes]
    # x264 já usa várias threads, mas não satura 8 núcleos sozinho: rodar alguns
    # clipes ao mesmo tempo aproveita o resto. ffmpeg é subprocesso, então
    # thread pool basta — não há GIL no caminho.
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futuros = {c["n"]: pool.submit(clipe_cena, proj, c["n"], duracoes[c["n"]],
                                       a.forcar, hw.x264_preset,
                                       c["papel"] != "cauda-ambiente")
                   for c in pendentes}
        resultados = {}
        for c in pendentes:                      # ordem do plano, não de conclusão
            resultados[c["n"]] = futuros[c["n"]].result()
            log(f"cena {c['n']:02d}  {duracoes[c['n']]:6.1f}s  {c['titulo']}")
    clipes = [resultados[c["n"]] for c in pendentes]

    print(f"[5/5] montagem")
    lista = lista_concat(proj / "build" / "concat.txt", clipes)
    mudo = proj / "build" / "video_mudo.mp4"
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", "-an", str(mudo)],
           "concat dos clipes")

    final = proj / "final.mp4"
    ffmpeg(["-i", str(mudo), "-i", str(mix), "-c:v", "copy", "-c:a", "copy",
            "-shortest", "-movflags", "+faststart", str(final)], "mux final")

    json.dump({"total_s": round(total, 2),
               "narrado_s": round(sum(v for k, v in duracoes.items()
                                      if not cauda or k != cauda["n"]), 2),
               "cenas": {str(k): round(v, 2) for k, v in duracoes.items()}},
              open(proj / "duracoes_render.json", "w", encoding="utf-8"), indent=2)

    print(f"\nOK — {final}")
    print(f"   {duracao(final)/60:.1f} min, {final.stat().st_size/1e6:.0f} MB")


if __name__ == "__main__":
    main()
