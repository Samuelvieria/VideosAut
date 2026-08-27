#!/usr/bin/env python3
"""s4 — gera legenda SRT alinhada, cena a cena.

    python -m pipeline.s4_legendas fase0/video-02 [--modelo small] [--forcar]

Requer: pip install faster-whisper

O Kokoro não devolve timestamps, então precisamos de ALINHAMENTO FORÇADO — não de
transcrição. Nós já temos o texto verdadeiro; o Whisper entra só para dizer QUANDO
cada trecho foi falado. O texto exibido vem sempre do roteiro, nunca da
transcrição.

Consequência prática: erro de reconhecimento é descartado pela reconciliação —
só o timing sobrevive. Usamos `large-v3` (~3 GB) porque ele tem limites de palavra
mais precisos, e limite de palavra é justamente o que aproveitamos. `small` também
funcionaria, com timing um pouco mais frouxo.

A reconciliação por distância de Levenshtein é adaptada do MoneyPrinterTurbo
(app/services/subtitle.py), MIT License, Copyright (c) 2024 Harry.
Simplificada: como o áudio já vem separado por cena, cada arquivo tem um
texto-verdade curto e conhecido — não é preciso casar o roteiro inteiro de uma vez.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import atualizado, carregar_plano, duracao, erro, log, marcar, projeto
from pipeline.perfil import perfil
from pipeline.s2_tts import blocos

PAUSA = 2.0  # tem de bater com PAUSA_ENTRE_CENAS do s5_render


def ts(s: float) -> str:
    h, r = divmod(max(0.0, s), 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"


def similaridade(a: str, b: str) -> float:
    """Levenshtein normalizada. Portado do MoneyPrinterTurbo (MIT)."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return 0.0
    ant = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            cur.append(min(ant[j + 1] + 1, cur[j] + 1, ant[j] + (ca != cb)))
        ant = cur
    return 1 - ant[-1] / max(len(a), len(b))


def frases(texto: str) -> list[str]:
    """Quebra o texto-verdade em frases exibíveis."""
    partes = re.split(r"(?<=[.!?…])\s+", " ".join(texto.split()))
    return [p.strip() for p in partes if p.strip()]


def segmentos_whisper(modelo, wav: Path) -> list[tuple[float, float, str]]:
    segs, _ = modelo.transcribe(str(wav), language="pt", beam_size=5,
                                word_timestamps=True, vad_filter=True,
                                vad_parameters=dict(min_silence_duration_ms=400))
    saida = []
    for s in segs:
        for w in (s.words or []):
            saida.append((w.start, w.end, w.word.strip()))
    return saida


def alinhar(palavras: list[tuple[float, float, str]], alvo: list[str]) -> list[tuple[float, float, str]]:
    """Casa cada frase do roteiro com a janela de palavras que mais se parece com ela.

    Avança um ponteiro pelas palavras transcritas, estendendo a janela enquanto a
    similaridade com a frase-alvo melhorar. O texto devolvido é SEMPRE o do roteiro.
    """
    fora, i = [], 0
    for frase in alvo:
        if i >= len(palavras):
            break
        ini = palavras[i][0]
        melhor_j, melhor_s, acc = i, -1.0, ""
        for j in range(i, min(len(palavras), i + len(frase.split()) * 3 + 6)):
            acc = (acc + " " + palavras[j][2]).strip()
            s = similaridade(frase.lower(), acc.lower())
            if s > melhor_s:
                melhor_s, melhor_j = s, j
        fim = palavras[melhor_j][1]
        fora.append((ini, fim, frase))
        i = melhor_j + 1
    return fora


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera SRT alinhado ao roteiro.")
    ap.add_argument("projeto")
    ap.add_argument("--modelo", default=None,
                    help="sobrescreve o modelo do perfil (ex.: small)")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()

    hw = perfil()
    modelo_nome = a.modelo or hw.whisper_modelo
    log(str(hw))

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    srt = proj / "legendas.pt-BR.srt"

    cenas = blocos(proj / "roteiro.md")
    wavs = [proj / "audio" / f"cena_{n:02d}.wav" for n, _, _ in cenas]
    faltando = [w.name for w in wavs if not w.exists()]
    if faltando:
        erro(f"faltam áudios: {', '.join(faltando)} — rode s2_tts antes")
    if not a.forcar and atualizado(srt, wavs, modelo_nome):
        log("legendas: já atualizadas")
        return

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        erro("faster-whisper não instalado.\n  source .venv/bin/activate && pip install faster-whisper")

    log(f"carregando '{modelo_nome}' em {hw.whisper_device}/{hw.whisper_compute}")
    modelo = WhisperModel(modelo_nome, device=hw.whisper_device,
                          compute_type=hw.whisper_compute)

    linhas, idx, offset = [], 1, 0.0
    for (n, titulo, corpo), wav in zip(cenas, wavs):
        palavras = segmentos_whisper(modelo, wav)
        for ini, fim, txt in alinhar(palavras, frases(corpo)):
            linhas.append(f"{idx}\n{ts(offset+ini)} --> {ts(offset+fim)}\n{txt}\n")
            idx += 1
        offset += duracao(wav) + PAUSA
        log(f"cena {n:02d}  {titulo}")

    srt.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    marcar(srt, wavs, modelo_nome)
    print(f"\nOK — {srt} ({idx-1} legendas)")
    print("Subir com captions.insert (legenda SOFT — nunca queimar, ver CLAUDE.md)")


if __name__ == "__main__":
    main()
