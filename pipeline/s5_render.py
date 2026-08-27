#!/usr/bin/env python3
"""s5 — monta o vídeo final a partir de imagens + narração por cena + ambiente.

    python -m pipeline.s5_render fase0/video-02 [--placeholder] [--forcar]

Arquitetura (medida em 26/08/2026, ver CLAUDE.md):
  - cada cena vira um clipe independente com fade para preto e GOP alinhado;
  - a montagem final é `concat -c copy` — instantânea, sem reencode;
  - a duração de cada clipe vem do ÁUDIO daquela cena, não do plano.

Por que as imagens ficam paradas: o estilo é pixel art. Zoom/pan contínuo
interpola subpixel e destrói a grade de pixels, que é o estilo inteiro. Movimento
correto para pixel art exige passo INTEIRO na grade da fonte — ver `movimento`.
"""
from __future__ import annotations
import argparse, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import (FFMPEG, atualizado, carregar_plano, duracao, erro,
                            ffmpeg, lista_concat, log, marcar, projeto)
from pipeline.perfil import perfil
from pipeline import ambiente as amb

FPS = 24
LARG, ALT = 1920, 1080
GOP = FPS * 2
PAUSA_ENTRE_CENAS = 2.0   # respiro entre cenas; também dá tempo do fade acontecer
FADE = 1.5
V_AMBIENTE = 0.9          # ganho do ambiente antes do ducking


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
        ffmpeg(["-f", "lavfi", "-i", f"color=c={cor}:s=640x360", "-frames:v", "1",
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


def _ambiente_cena(dest: Path, dur: float, cfg: dict) -> None:
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

    for canal in ("L", "R"):
        c = camadas[canal]
        if len(c) > 1:
            nos.append(f"{''.join(c)}amix=inputs={len(c)}:duration=longest:normalize=0[mix{canal}]")
        else:
            nos.append(f"{c[0]}anull[mix{canal}]")

    f = min(CROSSFADE, dur / 3)
    nos.append(f"[mixL][mixR]join=inputs=2:channel_layout=stereo,"
               f"afade=t=in:st=0:d={f:.2f},afade=t=out:st={dur-f:.2f}:d={f:.2f},"
               f"loudnorm=I=-24:TP=-3.0:LRA=9[out]")
    ffmpeg(["-filter_complex", ";".join(nos), "-map", "[out]",
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
                     sort_keys=True)
    if not forcar and atualizado(saida, [], cfg):
        log("ambiente: já atualizado")
        return saida

    d = proj / "build" / "amb_cenas"; d.mkdir(parents=True, exist_ok=True)
    partes = []
    for n in sorted(duracoes):
        alvo = d / f"amb_{n:02d}.wav"
        _ambiente_cena(alvo, duracoes[n], perfis.get(n, {}))
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


def mixar(proj: Path, narracao: Path, ambiente: Path, total_s: float, forcar: bool) -> Path:
    """Ducking sidechain + masterização a -18 LUFS (abaixo do alvo do YouTube).

    A voz fica MONO e centrada de propósito: narração é o foco e tem que vir de
    um ponto só. Quem ganha largura é o ambiente. Voz espalhada no campo estéreo
    soa difusa e atrapalha o adormecer, que é o oposto do que o vídeo existe para
    fazer.
    """
    saida = proj / "build" / "mix.m4a"
    cfg = f"amb={V_AMBIENTE};total={total_s:.1f};cena=v4;voz=eq+comp+sala"
    if not forcar and atualizado(saida, [narracao, ambiente], cfg):
        log("mix: já atualizado")
        return saida

    ffmpeg(["-i", str(narracao), "-i", str(ambiente), "-filter_complex",
            # voz mono -> duplicada nos dois canais (centro), estendida com silêncio
            # asplit explícito: a voz é consumida DUAS vezes (sidechain + mix). O
            # ffmpeg tolera reusar o label num grafo só-áudio, mas falha com
            # "matches no streams" se houver vídeo no mesmo filtergraph. Verificado
            # no ffmpeg 9.0.1. asplit funciona nos dois casos.
            # Cadeia de voz. TTS soa robótico por três motivos tratáveis:
            # médio-agudo estridente em 2-4 kHz, dinâmica plana demais, e ausência
            # de qualquer sala — a voz "flutua" fora de um espaço físico.
            f"[0:a]aformat=channel_layouts=mono,"
            f"highpass=f=80,"                       # tira ronco abaixo da voz
            f"equalizer=f=3000:t=q:w=1.4:g=-3,"     # corta a aspereza digital
            f"acompressor=threshold=-18dB:ratio=3:attack=15:release=250:knee=6,"
            f"aecho=0.92:0.85:23|37:0.10|0.07,"     # sala pequena, ~8% wet
            f"apad=whole_dur={total_s},"
            f"pan=stereo|c0=c0|c1=c0,asplit=2[voz_sc][voz_mix];"
            f"[1:a]aformat=channel_layouts=stereo,volume={V_AMBIENTE}[amb];"
            f"[amb][voz_sc]sidechaincompress=threshold=0.05:ratio=6:attack=200:release=1800[duck];"
            f"[duck][voz_mix]amix=inputs=2:duration=longest:normalize=0,"
            f"loudnorm=I=-18:TP=-2.0:LRA=7[out]",
            "-map", "[out]", "-t", f"{total_s}",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(saida)],
           "mix de áudio")
    marcar(saida, [narracao, ambiente], cfg)
    log(f"mix estéreo: {duracao(saida)/60:.1f} min")
    return saida


def clipe_cena(proj: Path, n: int, dur: float, forcar: bool, preset: str = "medium") -> Path:
    img = proj / "imagens" / f"cena_{n:02d}.png"
    if not img.exists():
        erro(f"falta {img}. Gere as imagens ou rode com --placeholder.")

    saida = proj / "build" / "clipes" / f"cena_{n:02d}.mp4"
    saida.parent.mkdir(parents=True, exist_ok=True)
    cfg = f"dur={dur:.2f};fps={FPS};fade={FADE};preset={preset}"
    if not forcar and atualizado(saida, [img], cfg):
        return saida

    f_out = max(0.0, dur - FADE)
    # flags=neighbor: upscale de pixel art tem que ser nearest, senão borra a grade
    vf = (f"scale={LARG}:{ALT}:flags=neighbor,format=yuv420p,"
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
    mix = mixar(proj, narracao, ambiente, total, a.forcar)

    jobs = a.jobs or hw.jobs
    print(f"[4/5] clipes de cena ({len(duracoes)}, {jobs} em paralelo)")
    pendentes = [c for c in plano["cenas"] if c["n"] in duracoes]
    # x264 já usa várias threads, mas não satura 8 núcleos sozinho: rodar alguns
    # clipes ao mesmo tempo aproveita o resto. ffmpeg é subprocesso, então
    # thread pool basta — não há GIL no caminho.
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futuros = {c["n"]: pool.submit(clipe_cena, proj, c["n"], duracoes[c["n"]],
                                       a.forcar, hw.x264_preset) for c in pendentes}
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
              open(proj / "duracoes_render.json", "w"), indent=2)

    print(f"\nOK — {final}")
    print(f"   {duracao(final)/60:.1f} min, {final.stat().st_size/1e6:.0f} MB")


if __name__ == "__main__":
    main()
