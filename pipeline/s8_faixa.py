"""Faixa de áudio em outro idioma para um vídeo já publicado.

    python -m pipeline.s8_faixa fase0/video-04 --lang en-US --voz Algieba
    python -m pipeline.s8_faixa fase0/video-04 --lang en-US --so-alinhar

O YouTube aceita até 6 faixas de áudio por vídeo e escolhe pela preferência do
espectador. Decidido em 05/09/2026 usar isso em vez de abrir um canal em inglês:
um vídeo com duas faixas acumula horas das DUAS audiências para UM patamar de
YPP, e faltam meses até 01/02/2027 com 3 inscritos. Ver
`docs/ingles-canal-separado.md`.

## A restrição que organiza este módulo inteiro

**A faixa tem que ter a duração do vídeo.** A página oficial diz "roughly the
same length"; as fontes secundárias dizem 1 segundo, e assumimos 1 segundo por
ser o lado seguro.

Isso não é um detalhe de exportação — é o que obriga o roteiro em inglês a ser
**adaptação presa ao tempo de cada cena**, e não roteiro reescrito livre. Uma
cena que estoura 4 segundos empurra tudo o que vem depois e desalinha o vídeo
inteiro, porque a imagem continua trocando no tempo do português.

Por isso o módulo ALINHA antes de mixar, e **recusa a cena que estoura** em vez
de cortá-la: aparar áudio corta palavra, e palavra cortada num vídeo de dormir é
pior que qualquer desvio de duração. Cena curta demais é preenchida com silêncio
— e silêncio, aqui, não é defeito.

## O que a faixa contém

Áudio completo, não só a voz: **narração em inglês + o mesmo ambiente + a mesma
cauda**. Ela substitui a trilha inteira quando o espectador troca de idioma. A
imagem e o ambiente não têm idioma, então só a narração muda — e é isso que faz
a conta fechar.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import carregar_plano, duracao, erro, log, projeto
from pipeline.s5_render import (PAUSA_ENTRE_CENAS, _cena_cauda, _cenas_narradas,
                                mixar, trilha_ambiente, trilha_narracao)

TOLERANCIA_S = 1.0        # o que o YouTube aceita de desvio na faixa inteira
FOLGA_CENA_S = 0.35       # estouro por cena que ainda dá para absorver

# Preencher com silêncio é legítimo para ajustar meio segundo. Não é para
# esconder uma adaptação curta demais: uma cena de 77 s com 34 s de silêncio
# soa como falha técnica, não como pausa. Acima disto o problema é o TEXTO,
# e quem escreve precisa saber — o alinhador não pode calar.
SILENCIO_DEMAIS = 0.12    # fração da cena


def _dur(p: Path) -> float:
    return duracao(p)


def alinhar(proj: Path, lang: str, cenas: list[dict]) -> list[tuple[int, float, float]]:
    """Ajusta cada cena do idioma alvo à duração da mesma cena em pt-BR.

    Devolve (n, dur_original, dur_alvo) para relatório. Curta demais ganha
    silêncio — um terço antes, o resto depois, para a fala não colar no corte da
    imagem. Longa demais é ERRO, com o excedente dito em segundos: quem escreveu
    precisa cortar palavras, e essa decisão é de quem escreve.

    **Não grava por cima de `audio-<lang>/`.** O alinhado sai em
    `build/audio-<lang>/`. Escrever no lugar apagaria o diagnóstico: na segunda
    rodada o desvio seria zero e o aviso de "faltam 72 palavras" sumiria, dando
    a impressão de que a adaptação estava certa. O relatório precisa continuar
    verdadeiro enquanto o texto não mudar.
    """
    import numpy as np, soundfile as sf
    curto = lang.split("-")[0]
    dir_alvo = proj / f"audio-{curto}"
    if not dir_alvo.is_dir():
        erro(f"não existe {dir_alvo} — rode o s2_tts com um plano em {lang} antes")
    dir_saida = proj / "build" / f"audio-{curto}"
    dir_saida.mkdir(parents=True, exist_ok=True)

    fora, estouros, vazias = [], [], []
    for c in cenas:
        n = c["n"]
        pt, alvo = proj / "audio" / f"cena_{n:02d}.wav", dir_alvo / f"cena_{n:02d}.wav"
        if not pt.is_file():
            erro(f"falta a cena em pt-BR: {pt}")
        if not alvo.is_file():
            erro(f"falta a cena em {lang}: {alvo}")
        d_pt, d_al = _dur(pt), _dur(alvo)
        fora.append((n, d_al, d_pt))
        if d_al > d_pt + FOLGA_CENA_S:
            estouros.append((n, d_al - d_pt))
            continue
        if d_pt - d_al > d_pt * SILENCIO_DEMAIS:
            vazias.append((n, d_pt - d_al, (d_pt - d_al) / d_pt))
        audio, sr = sf.read(alvo, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        falta = int(round((d_pt - d_al) * sr))
        if falta > 0:
            antes = np.zeros(falta // 3, dtype="float32")
            depois = np.zeros(falta - len(antes), dtype="float32")
            audio = np.concatenate([antes, audio, depois])
        elif falta < 0:             # dentro da folga: apara o rabo de silêncio
            audio = audio[:int(d_pt * sr)]
        sf.write(dir_saida / f"cena_{n:02d}.wav", audio, sr)

    if vazias:
        log(f"AVISO: {len(vazias)} cena(s) ficariam com muito silêncio — o texto "
            f"em {lang} está curto demais, não é problema de duração:")
        for n, falta, frac in vazias:
            log(f"    cena {n:02d}: faltam {falta:.0f}s ({frac*100:.0f}% da cena). "
                f"Acrescente ~{falta*127/60:.0f} palavras")
    if estouros:
        linhas = "\n".join(f"    cena {n:02d}: +{x:.1f}s" for n, x in estouros)
        erro(f"{len(estouros)} cena(s) estouram a duração do português:\n{linhas}\n"
             f"  A imagem troca no tempo do pt-BR, então esticar desalinha o vídeo.\n"
             f"  Corte palavras no roteiro em {lang} — não dá para aparar áudio\n"
             f"  sem cortar fala.")
    return fora


def main() -> None:
    ap = argparse.ArgumentParser(description="Faixa de áudio em outro idioma.")
    ap.add_argument("projeto")
    ap.add_argument("--lang", default="en-US")
    ap.add_argument("--so-alinhar", action="store_true",
                    help="só compara as durações e sai, sem mixar")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    narradas, cauda = _cenas_narradas(plano), _cena_cauda(plano)
    curto = a.lang.split("-")[0]

    print(f"\n[1/4] alinhando {a.lang} ao tempo do pt-BR")
    medidas = alinhar(proj, a.lang, narradas)
    desvio = sum(o - p for _, o, p in medidas)
    piores = sorted(medidas, key=lambda x: -abs(x[1] - x[2]))[:3]
    for n, o, p in piores:
        log(f"  cena {n:02d}: {o:6.1f}s contra {p:6.1f}s  ({o-p:+.1f}s)")
    log(f"desvio somado antes do alinhamento: {desvio:+.1f}s")
    if a.so_alinhar:
        return

    print(f"[2/4] narração em {a.lang}")
    narracao, _ = trilha_narracao(proj, narradas, a.forcar, f"build/audio-{curto}")

    # As durações de cena vêm do PORTUGUÊS de propósito: é o tempo em que a
    # imagem troca, e ele não pode mudar entre as faixas.
    duracoes = {c["n"]: _dur(proj / "audio" / f"cena_{c['n']:02d}.wav") + PAUSA_ENTRE_CENAS
                for c in narradas}
    if cauda:
        declarada = plano.get("cauda_ambiente_s")
        duracoes[cauda["n"]] = float(declarada) if declarada else 60.0
    total = sum(duracoes.values())

    print(f"[3/4] ambiente (o mesmo — ambiente não tem idioma)")
    ambiente = trilha_ambiente(proj, plano, duracoes, a.forcar)

    print(f"[4/4] mix e exportação")
    mix = mixar(proj, narracao, ambiente, total, a.forcar, plano.get("mixagem"))
    saida = proj / f"faixa.{curto}.m4a"
    # .m4a a 256 kbps / 48 kHz é o que o YouTube recomenda para faixa adicional
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(mix), "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                    str(saida)], check=True)

    d_faixa = _dur(saida)
    print(f"\nOK — {saida}  ({d_faixa/60:.1f} min)")
    final = proj / "final.mp4"
    if final.is_file():
        d_video = _dur(final)
        delta = d_faixa - d_video
        marca = "OK" if abs(delta) <= TOLERANCIA_S else "FORA DA TOLERÂNCIA"
        print(f"     vídeo {d_video/60:.1f} min · desvio {delta:+.2f}s — {marca}")
        if abs(delta) > TOLERANCIA_S:
            raise SystemExit(1)
    else:
        print(f"     {final.name} não está aqui — confira o desvio na máquina do render")
    print("     Studio -> vídeo -> Idiomas -> adicionar faixa de áudio")
    print("     E localize TÍTULO e DESCRIÇÃO: sem isso a faixa não destrava a busca")


if __name__ == "__main__":
    main()
