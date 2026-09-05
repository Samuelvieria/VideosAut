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


# ---------------------------------------------------------------------------
# NÍVEL POR CAMADA — medido em 05/09/2026, 25 s em intensidade 1.0
#
#     chuva     -17,8      insetos   -17,8
#     mar       -26,9      pano      -33,8
#     fogo      -31,8      areia     -37,1
#     vento     -37,3
#
# **`intensidade` NÃO é unidade comparável entre camadas.** As quatro originais
# já nasciam com 19,5 dB de espalhamento entre si, e isso nunca foi normalizado
# porque os video-02 e 03 foram aprovados de ouvido com esses valores — mexer
# agora mudaria som que já está publicado.
#
# O que fizemos com as camadas novas foi colocá-las DENTRO dessa faixa, e cada
# uma perto de quem faz o mesmo papel: `areia` perto de `vento` porque ela anda
# em cima dele, `pano` perto de `fogo` porque as duas são evento, `insetos`
# perto de `chuva` porque as duas são cobertor contínuo.
#
# Consequência prática para quem escreve plano.json: 0.4 em duas camadas
# diferentes não dá o mesmo volume. Os valores se acham de ouvido, no mixer.
# ---------------------------------------------------------------------------
# Camadas acrescentadas em 05/09/2026, quando a pauta deixou de ser só mar.
# O video-04 é deserto (Lawrence), o 05 é estrada romana à noite e o de ET nos
# anos 50 é campo americano — nenhum deles se atende com mar/chuva/fogo/vento.
#
# O desenho é o mesmo das camadas antigas e vale repetir por quê: cada evento é
# uma envoltória ataque-decaimento com período próprio, e os períodos são
# INCOMENSURÁVEIS, então nunca recaem em fase e não há loop audível.
# ---------------------------------------------------------------------------


def areia(dur: float, canal: str, intensidade: float = 1.0) -> list[str]:
    """Areia levada pelo vento — o que o vento CARREGA, não o vento.

    Fica numa banda mais alta que a do vento (1,5-9 kHz contra 200-2000) porque
    grão é pequeno: o que se ouve é o chiado fino por cima do sopro, não o sopro.
    Por isso `areia` quase nunca vai sozinha — ela pede `vento` embaixo.

    A modulação é soma de senos incomensuráveis, e não um só: com um período
    único o chiado vira tremolo audível, que num vídeo de dormir é pior que
    ruído parado.
    """
    s = 0 if canal == "L" else 1300
    d = 1.0 if canal == "L" else 1.043
    per = [(7.3 * d, 0.055), (11.9 * d, 0.040), (19.1 * d, 0.030)]
    mod = "+".join(f"{g}*sin(2*PI*t/{p})" for p, g in per)
    return [
        f"anoisesrc=color=pink:amplitude=1.0:r={SR}:d={dur}:seed={707+s}[ar{canal}0]",
        f"[ar{canal}0]highpass=f=1500,lowpass=f=9000,"
        f"volume=volume='{0.085*intensidade}+{intensidade}*({mod})':eval=frame[areia{canal}]",
    ]


def pano(dur: float, canal: str, intensidade: float = 1.0) -> list[str]:
    """Pano de tenda batendo. Evento, não cobertor — silencia entre um e outro.

    É a única camada nossa que **quase some** entre os eventos, de propósito: o
    mar nunca vai embora, a tenda vai. E é ela que dá a sensação de estar
    DENTRO de alguma coisa enquanto o deserto está do lado de fora — que é o
    que se quer de um som para dormir.

    O ataque (10-14) é bem mais lento que o do estalo de fogo (50-70). Estalo
    seco acorda; pano batendo, não.
    """
    s = 0 if canal == "L" else 1500
    d = 1.0 if canal == "L" else 1.071
    trens = [(5.3 * d, 0.0, 14.0, 3.2), (7.9 * d, 2.7, 12.0, 2.8),
             (11.3 * d, 5.1, 10.0, 2.4)]
    return [
        f"anoisesrc=color=brown:amplitude=1.0:r={SR}:d={dur}:seed={808+s}[pn{canal}0]",
        f"[pn{canal}0]highpass=f=300,lowpass=f=3000,"
        # 0,52 e não 0,13: medido em 05/09, a 0,13 o pano saía a -45,9 LUFS,
        # 14 dB abaixo da média das outras camadas — inaudível sob qualquer mix.
        f"volume=volume='0.016+{_soma_trens(trens, 0.52*intensidade)}':eval=frame[pano{canal}]",
    ]


def insetos(dur: float, canal: str, intensidade: float = 1.0) -> list[str]:
    """Coro de grilos ao longe. Serve estrada de noite e campo aberto.

    Grilo tem ALTURA, não só ruído — por volta de 4,5 kHz. Um seno puro nessa
    frequência soa a aparelho eletrônico; a solução é ruído branco por um
    passa-banda ressonante, que dá a altura sem a esterilidade do tom.

    Os pulsos são curtos (0,29 a 0,53 s) e incomensuráveis entre si: um período
    só viraria metrônomo, e três somados viram coro — que é o que se ouve de
    verdade quando os grilos são muitos e estão longe.
    """
    s = 0 if canal == "L" else 1700
    d = 1.0 if canal == "L" else 1.029
    trens = [(0.29 * d, 0.0, 90.0, 26.0), (0.37 * d, 0.11, 80.0, 22.0),
             (0.53 * d, 0.23, 70.0, 18.0)]
    return [
        f"anoisesrc=color=white:amplitude=1.0:r={SR}:d={dur}:seed={909+s}[in{canal}0]",
        f"[in{canal}0]bandpass=f=4500:width_type=q:w=14,volume=6.0,"
        f"volume=volume='{0.03*intensidade}+{_soma_trens(trens, 0.42*intensidade)}':eval=frame[insetos{canal}]",
    ]
