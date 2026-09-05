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


# Norma de legibilidade de legenda. Não é preferência: é o que a BBC, a Netflix
# e o guia da própria plataforma convergem em pedir, e o motivo é físico — o
# olho não lê linha mais longa que isso de relance, e bloco que fica menos de um
# segundo não dá tempo de sacada.
MAX_LINHA = 42        # caracteres por linha
MAX_LINHAS = 2
DUR_MIN = 1.0         # segundos
DUR_MAX = 7.0
MAX_BLOCO = MAX_LINHA * MAX_LINHAS


def _quebrar_linhas(txt: str) -> str:
    """Quebra em no máximo duas linhas, o mais equilibradas possível."""
    palavras = txt.split()
    if len(" ".join(palavras)) <= MAX_LINHA:
        return " ".join(palavras)
    melhor, dif = None, 10**9
    for k in range(1, len(palavras)):
        a, b = " ".join(palavras[:k]), " ".join(palavras[k:])
        if len(a) > MAX_LINHA or len(b) > MAX_LINHA:
            continue
        if abs(len(a) - len(b)) < dif:
            melhor, dif = (a, b), abs(len(a) - len(b))
    return "\n".join(melhor) if melhor else " ".join(palavras)


def _cabe(txt: str) -> bool:
    return all(len(l) <= MAX_LINHA for l in _quebrar_linhas(txt).split("\n"))


def _pedacos(txt: str, n: int) -> list[str]:
    """Parte em n trechos de tamanho parecido, sempre em fronteira de palavra."""
    if n <= 1:
        return [txt]
    alvo, pedacos, atual = len(txt) / n, [], ""
    for w in txt.split():
        if atual and len(atual) + 1 + len(w) > alvo and len(pedacos) < n - 1:
            pedacos.append(atual)
            atual = w
        else:
            atual = f"{atual} {w}".strip()
    if atual:
        pedacos.append(atual)
    return pedacos


def _fatiar(ini: float, fim: float, txt: str) -> list[tuple[float, float, str]]:
    """Parte um bloco grande demais, repartindo o tempo por caractere.

    Uma frase do roteiro pode ter 40 palavras — o `alinhar` devolve ela inteira
    como um bloco só, e sem esta passada virava legenda de 213 caracteres parada
    17 segundos na tela.

    O número de pedaços não é calculado, é PROCURADO: sobe até que cada pedaço
    caiba de fato em duas linhas e dentro do tempo máximo. Calcular errou nos
    dois eixos. Em caractere, porque 84 cabe em 84 mas não em 2x42 — a quebra
    consome um espaço e a fronteira de palavra é grossa. Em tempo, porque o
    tempo é repartido por caractere: um pedaço com 45% do texto fica com 45% da
    duração, e passa do teto mesmo quando a média não passaria.
    """
    dur, palavras = fim - ini, txt.split()
    n = 1
    while True:
        pedacos = _pedacos(txt, n)
        total = sum(len(x) for x in pedacos) or 1
        if all(_cabe(x) and dur * len(x) / total <= DUR_MAX for x in pedacos):
            break
        if n >= len(palavras):
            break
        n += 1

    if len(pedacos) == 1:
        return [(ini, fim, txt)]
    fora, t = [], ini
    for i, pedaco in enumerate(pedacos):
        f = fim if i == len(pedacos) - 1 else t + dur * len(pedaco) / total
        fora.append((t, f, pedaco))
        t = f
    return fora


def formatar(blocos_: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    """Aplica a norma: fatia o que é longo demais e estica o que é curto demais."""
    fora: list[tuple[float, float, str]] = []
    for ini, fim, txt in blocos_:
        fora.extend(_fatiar(ini, fim, " ".join(txt.split())))

    # Duração mínima, numa passada com cursor. Não basta esticar até o início do
    # próximo: no video-03 o alinhador empilhou "Cento e doze degraus." e "Vinte
    # anos." no MESMO instante, e qualquer limite tirado do vizinho deixaria os
    # dois com zero segundo — piscavam e sumiam. O cursor empurra quem vier pela
    # frente, e o empurrão morre sozinho no primeiro silêncio, que em vídeo de
    # sono nunca está longe. De quebra garante ordem e nenhuma sobreposição.
    t = 0.0
    for i, (ini, fim, txt) in enumerate(fora):
        ini = max(ini, t)
        fim = max(fim, ini + DUR_MIN)
        fora[i] = (ini, fim, txt)
        t = fim
    return [(i, f, _quebrar_linhas(t)) for i, f, t in fora]


def _ler_srt(srt: Path) -> list[tuple[float, float, str]]:
    def seg(t: str) -> float:
        h, m, resto = t.split(":")
        s_, ms = resto.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s_) + int(ms) / 1000

    fora = []
    for bloco in srt.read_text(encoding="utf-8").strip().split("\n\n"):
        linhas_ = [x for x in bloco.split("\n") if x.strip()]
        if len(linhas_) < 3:
            continue
        ini, fim = (seg(x) for x in linhas_[1].split(" --> "))
        fora.append((ini, fim, " ".join(linhas_[2:])))
    return fora


def reformatar(srt: Path) -> None:
    """Reaplica a norma num SRT já existente, sem rodar o whisper de novo.

    A formatação só mexe em texto e tempo — nada nela depende do áudio. Quando o
    SRT já foi gerado (o do video-03 saiu na workstation, em 30 min de whisper),
    refazer o alinhamento inteiro para arrumar quebra de linha é desperdício.

    Não regrava a marca de propósito: ela é hash das ENTRADAS (wavs + modelo),
    que não mudaram. Assim o `s4_legendas` normal continua dizendo "já
    atualizadas" e não atropela este arquivo na próxima passagem.
    """
    antes = _ler_srt(srt)
    depois = formatar(antes)
    linhas = [f"{i+1}\n{ts(ini)} --> {ts(fim)}\n{txt}\n"
              for i, (ini, fim, txt) in enumerate(depois)]
    srt.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    log(f"reformatado: {len(antes)} -> {len(depois)} blocos")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera SRT alinhado ao roteiro.")
    ap.add_argument("projeto")
    ap.add_argument("--modelo", default=None,
                    help="sobrescreve o modelo do perfil (ex.: small)")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--reformatar", action="store_true",
                    help="reaplica a norma de legibilidade no SRT existente, "
                         "sem whisper e sem áudio")
    a = ap.parse_args()

    if a.reformatar:
        srt_ = projeto(a.projeto) / "legendas.pt-BR.srt"
        if not srt_.is_file():
            erro(f"não existe: {srt_}")
        reformatar(srt_)
        return

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
        for ini, fim, txt in formatar(alinhar(palavras, frases(corpo))):
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
