"""Síntese procedural do ambiente: mar, chuva, fogo, vento.

Por que sintetizar em vez de usar gravação: áudio no YouTube passa por Content ID,
que faz match por impressão digital independentemente da licença comprada. Som
gerado não tem referência para casar — é a única fonte impossível de reivindicar.
Ver seção 3 do doc de viabilidade.

O mar aqui NÃO é ruído com modulação de amplitude. Isso soa como ruído pulsando,
não como rebentação. Uma onda real é um evento discreto com três partes:

    grave que cresce  ->  estouro de banda larga  ->  cauda sibilante decaindo

Cada trem de ondas é uma envoltória ataque-decaimento repetida com período próprio.
Somando trens de períodos incomensuráveis (8,3 / 11,7 / 17,1 s), as ondas nunca
recaem em fase — não há loop audível, e o ritmo fica irregular como surf de verdade.
"""
from __future__ import annotations

SR = 48000


def _env(periodo: float, offset: float, ataque: float, decai: float) -> str:
    """Envoltória ataque-decaimento de UM trem de ondas, como expressão do ffmpeg.

    `ataque` alto = estouro seco; `decai` alto = cauda curta. A fase corre de 0 ao
    período e reinicia, então cada ciclo é uma onda.
    """
    ph = f"mod(t+{offset},{periodo})"
    return f"(1-exp(-{ataque}*{ph}))*exp(-{decai}*{ph})"


def _soma_trens(trens: list[tuple[float, float, float, float]], ganho: float) -> str:
    termos = "+".join(_env(*t) for t in trens)
    return f"{ganho}*({termos})"


# (período, offset, ataque, decaimento) — períodos sem múltiplo comum
_TRENS_GRAVE = [(8.3, 0.0, 5.0, 0.85), (11.7, 3.1, 4.0, 0.70), (17.1, 7.4, 3.0, 0.55)]
# o estouro chega um pouco depois do grave: offset deslocado ~0,5 s
_TRENS_CRASH = [(8.3, -0.5, 26.0, 1.7), (11.7, 2.6, 22.0, 1.5), (17.1, 6.9, 18.0, 1.3)]


def mar(dur: float, canal: str, intensidade: float = 1.0) -> list[str]:
    """Devolve os nós de filtro do mar para um canal ('L' ou 'R').

    Os dois canais usam seeds e desvios de período diferentes: a mesma onda não
    chega igual nos dois ouvidos, e a imagem estéreo anda em vez de colar no centro.
    """
    d = 1.0 if canal == "L" else 1.061          # desvio de período por canal
    s = 0 if canal == "L" else 500
    trens_g = [(p * d, o, a, k) for p, o, a, k in _TRENS_GRAVE]
    trens_c = [(p * d, o, a, k) for p, o, a, k in _TRENS_CRASH]

    # fundo constante: o mar nunca some entre ondas
    fundo = 0.16 * intensidade
    g_grave = 0.62 * intensidade
    g_crash = 0.30 * intensidade

    return [
        # corpo grave da onda
        f"anoisesrc=color=brown:amplitude=1.0:r={SR}:d={dur}:seed={101+s}[mg{canal}0]",
        f"[mg{canal}0]lowpass=f=260,highpass=f=28,"
        f"volume=volume='{fundo}+{_soma_trens(trens_g, g_grave)}':eval=frame[mg{canal}]",
        # estouro / espuma, banda larga
        f"anoisesrc=color=pink:amplitude=1.0:r={SR}:d={dur}:seed={202+s}[mc{canal}0]",
        f"[mc{canal}0]highpass=f=700,lowpass=f=9000,"
        f"volume=volume='0.02+{_soma_trens(trens_c, g_crash)}':eval=frame[mc{canal}]",
        f"[mg{canal}][mc{canal}]amix=inputs=2:duration=longest:normalize=0[mar{canal}]",
    ]


def chuva(dur: float, canal: str, intensidade: float = 1.0, abafada: bool = False) -> list[str]:
    """Chuva. `abafada=True` = ouvida de dentro, através de parede/janela."""
    s = 0 if canal == "L" else 700
    per = 23.0 if canal == "L" else 19.7
    if abafada:
        banda, base = "highpass=f=120,lowpass=f=1400", 0.20 * intensidade
    else:
        banda, base = "highpass=f=600,lowpass=f=7000", 0.30 * intensidade
    return [
        f"anoisesrc=color=white:amplitude=1.0:r={SR}:d={dur}:seed={303+s}[ch{canal}0]",
        f"[ch{canal}0]{banda},"
        f"volume=volume='{base}+{0.06*intensidade}*sin(2*PI*t/{per})':eval=frame[chuva{canal}]",
    ]


def fogo(dur: float, canal: str, intensidade: float = 1.0) -> list[str]:
    """Lareira/fornalha: estalos irregulares sobre um sopro grave."""
    s = 0 if canal == "L" else 900
    trens = [(1.7, 0.0, 60.0, 9.0), (2.9, 0.9, 70.0, 11.0), (4.3, 2.2, 50.0, 7.0)]
    d = 1.0 if canal == "L" else 1.037
    trens = [(p * d, o, a, k) for p, o, a, k in trens]
    return [
        f"anoisesrc=color=brown:amplitude=1.0:r={SR}:d={dur}:seed={404+s}[fg{canal}0]",
        f"[fg{canal}0]lowpass=f=700,volume=volume='{0.12*intensidade}':eval=frame[fg{canal}]",
        f"anoisesrc=color=white:amplitude=1.0:r={SR}:d={dur}:seed={505+s}[fc{canal}0]",
        f"[fc{canal}0]highpass=f=1200,lowpass=f=8000,"
        f"volume=volume='0.01+{_soma_trens(trens, 0.16*intensidade)}':eval=frame[fc{canal}]",
        f"[fg{canal}][fc{canal}]amix=inputs=2:duration=longest:normalize=0[fogo{canal}]",
    ]


def vento(dur: float, canal: str, intensidade: float = 1.0) -> list[str]:
    """Vento: banda estreita varrendo devagar, sem ritmo perceptível."""
    s = 0 if canal == "L" else 1100
    per = 31.0 if canal == "L" else 27.3
    return [
        f"anoisesrc=color=pink:amplitude=1.0:r={SR}:d={dur}:seed={606+s}[vt{canal}0]",
        f"[vt{canal}0]highpass=f=200,lowpass=f=2000,"
        f"volume=volume='{0.10*intensidade}+{0.08*intensidade}*sin(2*PI*t/{per})':eval=frame[vento{canal}]",
    ]
