"""Ativos do CANAL, não de um vídeo: foto de perfil, banner.

    python -m pipeline.canal --avatar          # três candidatas + folha de contato
    python -m pipeline.canal --avatar --forcar

Separado dos estágios s1..s7 de propósito: aqueles processam UM vídeo e são
idempotentes por projeto. Isto aqui roda uma vez por canal, ou quando a
identidade muda.

## Por que três candidatas e não uma

Mesmo motivo das miniaturas (`s5b_thumbs.py`): o Samuel julga de olho, e
julgar bem exige comparar. Uma imagem sozinha sempre parece boa.

## Por que uma delas NÃO é pixel art

A foto de perfil é onde o classificador de audiência do YouTube e o espectador
formam a primeira impressão do canal. Em 05/09/2026 registramos que **pixel art
é linguagem de jogo** e puxa para o lado errado do risco Made for Kids, que
neste nicho desliga anúncio personalizado, comentários e notificação de
inscrito. Manter a pixel art nas CENAS é uma decisão tomada; fazer dela também
o avatar seria concentrar o risco justamente no ponto mais visível. Por isso a
folha traz uma pixel art, uma pintura e um ícone mínimo — e a escolha é dele.

## O que o formato exige

O YouTube recorta em CÍRCULO e exibe a 88px na página do canal e a 48px ou
menos em comentário e busca. Isso manda: assunto centralizado com margem, UMA
forma dominante, e contraste alto entre a luz e o fundo. Detalhe fino some.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import log
from pipeline.config import obter
from pipeline.s3_imagens import gerar

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "fase0" / "_canal"
LADO = 1024          # quadrado; a fal.ai não entrega abaixo de 512 num eixo

# O fio comum dos dois vídeos publicados é o mesmo: uma luz quente no escuro,
# sobre água. É o que o canal é, e lê a 48px.
AVATARES = {
    "A_pixel": (
        "16-bit pixel art, a lone stone lighthouse tower at night seen from far away, "
        "one small warm amber light burning at the top, dark blue calm sea below, "
        "deep navy sky, centered composition with margin around the tower, "
        "limited dark palette of navy and amber, dithering, no text, no letters",
        7101,
        "pixel art — mesma linguagem das cenas dos vídeos",
    ),
    "B_pintura": (
        "oil painting, a single warm amber lantern glowing above dark still water at "
        "night, its reflection stretching down, deep blue-black background, soft "
        "painterly brushwork, quiet and minimal, centered with margin, no figures, "
        "no buildings, no text, no letters",
        7102,
        "pintura atmosférica — lê como adulto, sem risco de leitura infantil",
    ),
    "C_icone": (
        "minimal flat icon design, a warm amber crescent moon low over dark still "
        "water, its reflection a single vertical line, deep navy background, only two "
        "colors, very high contrast, geometric and simple, centered with wide margin, "
        "no text, no letters",
        7103,
        "ícone mínimo — o único que ainda lê a 24px",
    ),
    # SEGUNDA RODADA. A primeira ensinou que a 48px só sobrevive forma sólida com
    # contraste alto — a pixel art e a pintura viraram borrão escuro.
    #
    # CORREÇÃO de 05/09: eu havia escrito aqui que o modelo "ignorou pixel art e
    # entregou farol realista". Errado — eu julguei pela miniatura da folha. Em
    # tamanho real o A é pixel art legítima, com blocos visíveis na torre e o
    # reflexo em traços discretos. O Samuel viu e corrigiu. O que falha no A não
    # é o estilo, é a COMPOSIÇÃO: assunto pequeno no quadro, azul escuro sobre
    # azul escuro. Ver a terceira rodada.
    "D_farol": (
        "minimal flat icon, bold silhouette of a lighthouse tower, a single warm "
        "amber beam of light sweeping out from its top across a deep navy field, "
        "only two colors, very high contrast, geometric, thick simple shapes, "
        "centered with wide margin, no text, no letters",
        7104,
        "farol como ícone — diz o que narramos, não só 'sono'",
    ),
    "E_janela": (
        "minimal flat icon, a dark tower silhouette against a deep navy field with "
        "one single warm amber lit window glowing near the top, only two colors, "
        "very high contrast, geometric, thick simple shapes, centered with wide "
        "margin, no text, no letters",
        7105,
        "uma janela acesa — a imagem mais literal de 'alguém acordado por você'",
    ),
    "F_lua_agua": (
        "minimal flat icon, a large warm amber full moon sitting low, its wide "
        "reflection spreading across dark still water below in horizontal bands, "
        "deep navy background, only two colors, very high contrast, geometric, "
        "centered with wide margin, no text, no letters",
        7106,
        "lua cheia sobre água — mais peso que a crescente, ainda lê pequeno",
    ),
}

# TERCEIRA RODADA — pixel art, agora composta para o recorte circular.
# O A provou que o estilo funciona; o que não funcionava era o enquadramento.
# Aqui o assunto OCUPA o quadro e a luz quente é grande o bastante para
# sobreviver ao recorte de 48px. Mesma paleta navy/âmbar dos vídeos.
PIXEL = {
    "G_lanterna": (
        "16-bit pixel art, extreme close-up of the top of a lighthouse at night, "
        "the lantern room filling most of the frame, one big glowing warm amber "
        "window, dark navy night sky behind, chunky visible pixels, large simple "
        "blocks, limited palette of navy and amber, very high contrast, centered, "
        "no text, no letters",
        7201,
        "a lanterna de perto — a luz vira a forma dominante",
    ),
    "H_lua_mar": (
        "16-bit pixel art, a huge warm amber crescent moon filling the upper half "
        "of the frame above a dark navy pixel sea, dashed pixel reflection on the "
        "water, chunky visible pixels, limited palette of navy and amber, very high "
        "contrast, centered, no text, no letters",
        7202,
        "lua grande sobre mar de pixel — a mais legível de todas",
    ),
    "I_farol_lua": (
        "16-bit pixel art, a small dark lighthouse silhouette on the horizon in "
        "front of a huge warm amber full moon rising behind it, dark navy pixel sea "
        "below with dashed reflection, chunky visible pixels, limited palette, very "
        "high contrast, centered, no text, no letters",
        7203,
        "o farol do A, mas recortado contra uma lua que carrega o contraste",
    ),
    "J_janela": (
        "16-bit pixel art, close-up of a dark stone tower wall at night, one large "
        "warm amber lit window in the center filling much of the frame, chunky "
        "visible pixels, deep navy and amber palette, very high contrast, centered, "
        "no text, no letters",
        7204,
        "só a janela acesa — alguém ficou acordado por você",
    ),
}

SERIES = {"icone": AVATARES, "pixel": PIXEL}


def folha_contato(arquivos: list[tuple[str, Path]], saida: Path) -> None:
    """Junta as candidatas lado a lado, e MOSTRA cada uma também em 48px.

    Ver a arte em tamanho grande engana: escolhe-se pela beleza do detalhe que
    ninguém nunca verá. A segunda fileira é o tamanho real de um comentário.
    """
    from PIL import Image, ImageDraw
    n, lado, peq, pad = len(arquivos), 320, 48, 24
    larg = n * lado + (n + 1) * pad
    folha = Image.new("RGB", (larg, lado + peq + 3 * pad), (18, 20, 28))
    d = ImageDraw.Draw(folha)
    for i, (nome, caminho) in enumerate(arquivos):
        x = pad + i * (lado + pad)
        im = Image.open(caminho).convert("RGB")
        # círculo, que é como o YouTube exibe
        for alvo, y, tam in ((lado, pad, lado), (peq, pad * 2 + lado, peq)):
            c = im.resize((tam, tam), Image.LANCZOS)
            mask = Image.new("L", (tam, tam), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, tam - 1, tam - 1), fill=255)
            folha.paste(c, (x + (lado - tam) // 2, y), mask)
        d.text((x, lado + pad + 6), nome, fill=(200, 200, 210))
    folha.save(saida)


def main() -> None:
    ap = argparse.ArgumentParser(description="Ativos do canal.")
    ap.add_argument("--avatar", action="store_true")
    ap.add_argument("--serie", default="icone", choices=list(SERIES))
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    if not a.avatar:
        ap.error("use --avatar")

    DESTINO.mkdir(parents=True, exist_ok=True)
    chave = obter("FAL_KEY")
    feitos = []
    for nome, (prompt, seed, porque) in SERIES[a.serie].items():
        f = DESTINO / f"avatar_{nome}.png"
        if f.is_file() and not a.forcar:
            log(f"já existe {nome}")
        else:
            f.write_bytes(gerar(prompt, seed, chave, LADO, LADO))
            log(f"gerada {nome} — {porque}")
        feitos.append((nome, f))
    folha_contato(feitos, DESTINO / f"avatar_contato_{a.serie}.png")
    print(f"\nOK — {len(feitos)} candidatas em {DESTINO}")
    print(f"     folha: {DESTINO / f'avatar_contato_{a.serie}.png'} (a fileira de baixo é o tamanho real)")


if __name__ == "__main__":
    main()
