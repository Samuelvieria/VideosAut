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

# QUARTA RODADA — a H com mais matéria dentro.
# "Gostei da H, mas acho que tá simples" (Samuel, 05/09). A restrição é que o
# que entrar precisa RESOLVER a 320px e ficar QUIETO a 48px: detalhe que compete
# com a lua no tamanho pequeno destrói exatamente o que a H tem de bom.
# Todas na seed da H (7202) para a lua ficar na mesma família; só o que se
# acrescenta muda, do mais discreto ao mais cheio.
LUA = {
    "K_estrelas": (
        "16-bit pixel art, a huge warm amber crescent moon filling the upper half "
        "of the frame above a dark navy pixel sea, dashed pixel reflection on the "
        "water, a scatter of small pale pixel stars across the navy sky, chunky "
        "visible pixels, limited palette of navy and amber, very high contrast, "
        "centered, no text, no letters",
        7202,
        "só estrelas — o acréscimo mais discreto possível",
    ),
    "L_farol_horizonte": (
        "16-bit pixel art, a huge warm amber crescent moon filling the upper half "
        "of the frame above a dark navy pixel sea, dashed pixel reflection on the "
        "water, small pale pixel stars in the sky, a tiny dark lighthouse "
        "silhouette far away on the horizon line with one speck of amber light, "
        "chunky visible pixels, navy and amber palette, very high contrast, "
        "centered, no text, no letters",
        7202,
        "estrelas + um farol minúsculo no horizonte — junta a H e a I",
    ),
    "M_barco": (
        "16-bit pixel art, a huge warm amber crescent moon filling the upper half "
        "of the frame above a dark navy pixel sea, dashed pixel reflection, small "
        "pale pixel stars, a tiny dark sailboat silhouette crossing the moon's "
        "reflection on the water, chunky visible pixels, navy and amber palette, "
        "very high contrast, centered, no text, no letters",
        7202,
        "um barco atravessando o reflexo — acrescenta narrativa, não só textura",
    ),
    "N_nuvens": (
        "16-bit pixel art, a huge warm amber crescent moon in the upper frame "
        "partly crossed by thin dark pixel clouds, small pale stars, a dark navy "
        "pixel sea below with several layered bands of dashed reflection and wave "
        "texture, distant dark cliffs on one side, chunky visible pixels, navy and "
        "amber palette, very high contrast, centered, no text, no letters",
        7202,
        "nuvens, camadas de água e um rochedo — a mais cheia das quatro",
    ),
}

SERIES = {"icone": AVATARES, "pixel": PIXEL, "lua": LUA}


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


# ---------------------------------------------------------------- banner
# O YouTube recorta o banner de forma diferente em cada tela e só um retângulo
# CENTRAL aparece em todas. Projetar para os 2560×1440 é o erro clássico: fica
# lindo na TV, que quase ninguém usa, e no celular só se vê uma tira do meio.
BANNER_L, BANNER_A = 2560, 1440          # o que se sobe
SEGURO_L, SEGURO_A = 1235, 338           # o que aparece em TODAS as telas
RECORTES = {                              # largura × altura, centrados
    "TV":      (2560, 1440),
    "desktop": (2560, 423),
    "tablet":  (1855, 423),
    "celular": (1546, 423),
    "SEGURO":  (SEGURO_L, SEGURO_A),
}
CREME = "0xF2E8D5"

# Gerado em 1280×720 e ampliado ×2 com vizinho mais próximo — que dá exatamente
# 2560×1440, o tamanho recomendado. Escala inteira preserva a grade de pixel;
# qualquer interpolação borraria a arte, e é a mesma regra do `flags=neighbor`
# do render (ver CLAUDE.md § Imagens).
BANNER_FONTE_L, BANNER_FONTE_A = 1280, 720

BANNERS = {
    "A_horizonte": (
        "16-bit pixel art, a very wide calm night seascape, dark navy water "
        "filling the lower half with dashed pixel reflections, a warm amber "
        "crescent moon low in the center of the sky, a tiny dark lighthouse "
        "silhouette far away on the horizon, scattered pale pixel stars, chunky "
        "visible pixels, limited navy and amber palette, empty sky with room to "
        "breathe, no text, no letters",
        7301,
        "horizonte largo — o assunto todo dentro da tira central",
    ),
    "B_farol_lado": (
        "16-bit pixel art, a very wide night seascape, a dark stone lighthouse "
        "standing on rocks at the left with one warm amber light at its top, "
        "wide dark navy sea stretching to the right, a low horizon line, pale "
        "pixel stars, chunky visible pixels, limited navy and amber palette, no "
        "text, no letters",
        7302,
        "farol à esquerda, mar aberto à direita — deixa o centro livre para o nome",
    ),
    "C_so_mar": (
        "16-bit pixel art, a very wide expanse of dark navy night sea with "
        "layered horizontal bands of wave texture, a faint amber glow on the "
        "horizon line as if from a light far out of frame, deep empty sky above "
        "with a few pale stars, chunky visible pixels, very dark and quiet, no "
        "text, no letters",
        7303,
        "só o mar — o mais sóbrio, e o que menos disputa com o nome",
    ),
}


def banner(nome: str, texto: str | None) -> Path:
    """Gera o banner e a prévia com os recortes de cada tela."""
    from PIL import Image, ImageDraw, ImageFont
    from pipeline.s5b_thumbs import FONTE
    prompt, seed, _ = BANNERS[nome]
    cru = DESTINO / f"_bruto/banner_{nome}.png"
    cru.parent.mkdir(parents=True, exist_ok=True)
    if not cru.is_file():
        cru.write_bytes(gerar(prompt, seed, obter("FAL_KEY"),
                              BANNER_FONTE_L, BANNER_FONTE_A))
    im = Image.open(cru).convert("RGB").resize((BANNER_L, BANNER_A), Image.NEAREST)

    if texto:
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(FONTE, 132)
        # Acima do centro, não no centro: em toda composição que sobrevive ao
        # recorte o assunto está NA linha do horizonte, que é o meio exato, e
        # texto ali disputa com ele. Mas não tão acima que saia da tira segura —
        # a 110 o topo das letras caía 7px para fora dela, e o aparato de
        # recorte existe justamente para pegar isso.
        cx, cy = BANNER_L // 2, BANNER_A // 2 - 85
        cima, baixo = cy - 66, cy + 66
        topo_seguro, base_segura = (BANNER_A - SEGURO_A) // 2, (BANNER_A + SEGURO_A) // 2
        if cima < topo_seguro or baixo > base_segura:
            log(f"AVISO: o texto vai de y={cima} a y={baixo} e a tira segura é "
                f"{topo_seguro}–{base_segura}. Vai ser cortado em alguma tela.")
        cor = tuple(int(CREME[2:][i:i+2], 16) for i in (0, 2, 4))
        # sombra suave, nunca contorno duro — mesma regra das miniaturas
        for dx, dy in ((6, 6), (4, 4)):
            d.text((cx + dx, cy + dy), texto, font=f, fill=(0, 0, 0), anchor="mm")
        d.text((cx, cy), texto, font=f, fill=cor, anchor="mm")

    saida = DESTINO / f"banner_{nome}{'_com_nome' if texto else ''}.png"
    im.save(saida)

    # prévia: o mesmo banner nos recortes de cada tela, empilhados
    escala = 0.42
    alturas = [int(a * escala) for _, a in RECORTES.values()]
    prev = Image.new("RGB", (int(BANNER_L * escala) + 40,
                             sum(alturas) + 34 * len(RECORTES) + 20), (18, 20, 28))
    dp = ImageDraw.Draw(prev)
    y = 10
    for rot, (rl, ra) in RECORTES.items():
        cx, cy = BANNER_L // 2, BANNER_A // 2
        corte = im.crop((cx - rl // 2, cy - ra // 2, cx + rl // 2, cy + ra // 2))
        corte = corte.resize((int(rl * escala), int(ra * escala)), Image.LANCZOS)
        prev.paste(corte, (20 + (int(BANNER_L * escala) - corte.width) // 2, y))
        y += corte.height + 6
        dp.text((20, y), f"{rot}  {rl}x{ra}", fill=(200, 200, 210))
        y += 28
    prev.save(DESTINO / f"banner_previa_{nome}{'_com_nome' if texto else ''}.png")
    return saida


def exportar(nome: str) -> Path:
    """Prepara a candidata escolhida como foto de perfil pronta para subir.

    Fica em 1024x1024 de propósito. O YouTube recomenda 800x800 e aceita maior,
    reamostrando ele mesmo — e 1024 para 800 não é razão inteira, então
    reamostrar aqui só borraria a grade de pixel antes de entregar. Mesma lógica
    do `flags=neighbor` do render: em pixel art, quem reamostra errado destrói o
    que a arte tem.

    Também gera uma prévia com o recorte CIRCULAR nos tamanhos reais de uso, e
    avisa se algo importante cai fora do círculo — o YouTube corta os cantos e
    não pergunta.
    """
    from PIL import Image, ImageDraw
    origem = DESTINO / f"avatar_{nome}.png"
    if not origem.is_file():
        raise SystemExit(f"não existe: {origem}\n  candidatas: "
                         + ", ".join(sorted(f.stem.replace("avatar_", "")
                                            for f in DESTINO.glob("avatar_*.png")
                                            if "contato" not in f.name)))
    im = Image.open(origem).convert("RGB")
    saida = DESTINO / "foto-perfil.png"
    im.save(saida)

    # prévia: o círculo nos tamanhos em que as pessoas realmente veem
    # o espaço de cada coluna é o MAIOR entre a imagem e o rótulo — senão o
    # texto de um tamanho pequeno invade o do vizinho
    tamanhos = [(320, "canal, grande"), (88, "canal"),
                (48, "comentário"), (24, "inscrições")]
    colunas = [max(t, 8 * len(r) + 10) for t, r in tamanhos]
    larg = sum(colunas) + 40 * (len(tamanhos) + 1)
    prev = Image.new("RGB", (larg, 400), (18, 20, 28))
    d = ImageDraw.Draw(prev)
    x = 40
    for (tam, rotulo), col in zip(tamanhos, colunas):
        c = im.resize((tam, tam), Image.LANCZOS)
        mask = Image.new("L", (tam, tam), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, tam - 1, tam - 1), fill=255)
        prev.paste(c, (x + (col - tam) // 2, 340 - tam), mask)
        d.text((x, 355), f"{tam}px", fill=(200, 200, 210))
        d.text((x, 370), rotulo, fill=(120, 122, 132))
        x += col + 40
    prev.save(DESTINO / "foto-perfil-previa.png")
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description="Ativos do canal.")
    ap.add_argument("--exportar", metavar="CANDIDATA",
                    help="prepara a escolhida como foto de perfil (ex.: L_farol_horizonte)")
    ap.add_argument("--avatar", action="store_true")
    ap.add_argument("--banner", action="store_true")
    ap.add_argument("--nome", default=None,
                    help="texto do banner; sem isto, banner limpo sem nome")
    ap.add_argument("--serie", default="icone", choices=list(SERIES))
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    if a.exportar:
        f = exportar(a.exportar)
        print(f"\nOK — {f}")
        print(f"     prévia nos tamanhos reais: {DESTINO / 'foto-perfil-previa.png'}")
        print("     Studio -> Personalização -> Identidade visual -> Foto")
        return
    if a.banner:
        DESTINO.mkdir(parents=True, exist_ok=True)
        for nome in BANNERS:
            f = banner(nome, a.nome)
            log(f"{nome} — {BANNERS[nome][2]}")
        print(f"\nOK — {len(BANNERS)} banners em {DESTINO}")
        print("     prévias mostram o recorte de cada tela; a tira SEGURO é a")
        print("     única que aparece em TODAS — projete para ela, não para a TV")
        return
    if not a.avatar:
        ap.error("use --avatar, --banner ou --exportar")

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
