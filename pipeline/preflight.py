"""Confere um projeto ANTES de gastar dinheiro ou tempo de máquina.

    python -m pipeline.preflight fase0/video-03

Existe porque quase todo erro caro deste projeto foi de coisa conferível antes:

- o `s2_tts` sintetizando um bloco `## Cena` de cauda e falando "sem narração"
- 30 min de CPU gastos com `speed` abaixo do piso que destrói o acento tonal
- 47 min de vídeo descobertos depois de gerar, porque ninguém multiplicou
  palavras por ppm antes
- cenas sem `prompt` que só apareceriam no meio de uma geração paga
- um cue de prompt já corrigido num vídeo voltando no seguinte

Cada verificação abaixo corresponde a um desses. Sai com código 1 se houver
qualquer ERRO, para poder entrar numa sequência do estúdio como primeiro passo.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import carregar_plano, projeto
from pipeline.s2_tts import blocos

PISO_SPEED = 0.85          # medido 04/09/2026; ver skill § Ritmo de narração
PPM_MEDIDO = {0.60: 106, 0.85: 148, 0.95: 167}
FAIXA_MERCADO = (65, 170)  # minutos; docs/mercado.md §2
USD_POR_MP = 0.005         # fal.ai Z-Image-Turbo
BRL_POR_USD = 5.10

# Cues que já custaram uma rodada de erro. Espelha estudio/db/personas.py, mas
# o pipeline NÃO importa de estudio/ (ver a regra em estudio/main.py), então a
# lista vive nos dois lugares de propósito.
# `so_base=True` marca a regra que vale só para o estilo_base. Hora do dia é o
# caso: no estilo_base é erro (vale para todas as cenas), mas no prompt DA CENA
# é obrigatório — é a cena que diz a luz dela.
CUES_RUINS = [
    (r"\bgam(e|ing)\b[\w\s]{0,20}\bart\b|\btitle\s+screen\b",
     "linguagem de arte de jogo — escreveu o título dentro da imagem no video-02", False),
    (r"\b(at|in\s+the|late)\s+(night|dawn|dusk|noon|sunset|sunrise|midnight|"
     r"morning|afternoon|evening)\b|\b(daytime|nighttime)\b",
     "hora do dia no estilo_base vale para TODAS as cenas e contradiz as que "
     "se passam em outro momento", True),
    (r"\b(no|without|never|sem)\s+\w{0,12}\s*(text|watermark|logo|letter|title)",
     "negação em prompt positivo pede o que nega", False),
]


class Resultado:
    def __init__(self) -> None:
        self.linhas: list[tuple[str, str]] = []

    def ok(self, msg: str) -> None: self.linhas.append(("ok", msg))
    def aviso(self, msg: str) -> None: self.linhas.append(("aviso", msg))
    def erro(self, msg: str) -> None: self.linhas.append(("ERRO", msg))

    @property
    def erros(self) -> int:
        return sum(1 for n, _ in self.linhas if n == "ERRO")

    def imprimir(self) -> None:
        larg = max((len(n) for n, _ in self.linhas), default=4)
        for nivel, msg in self.linhas:
            print(f"  {nivel:<{larg}}  {msg}")


def _ppm(speed: float) -> float:
    """Interpola o ppm medido. Fora da faixa medida, extrapola linear."""
    xs = sorted(PPM_MEDIDO)
    if speed <= xs[0]:
        return PPM_MEDIDO[xs[0]] * speed / xs[0]
    for a, b in zip(xs, xs[1:]):
        if speed <= b:
            t = (speed - a) / (b - a)
            return PPM_MEDIDO[a] + t * (PPM_MEDIDO[b] - PPM_MEDIDO[a])
    return PPM_MEDIDO[xs[-1]] * speed / xs[-1]


def conferir(proj: Path) -> Resultado:
    r = Resultado()
    plano = carregar_plano(proj)
    cenas = plano.get("cenas") or []

    # ---- roteiro x plano
    rot = proj / "roteiro.md"
    if not rot.is_file():
        r.erro("falta roteiro.md")
        return r
    b = blocos(rot)
    sem_n = [i for i, c in enumerate(cenas, 1) if "n" not in c]
    if sem_n:
        r.erro(f"cenas sem o campo `n` na posição {sem_n[:6]} — o pipeline nomeia "
               f"os arquivos por ele")
        cenas = [{**c, "n": c.get("n", i)} for i, c in enumerate(cenas, 1)]
    narradas = [c for c in cenas if c.get("papel") != "cauda-ambiente"]
    if len(b) != len(narradas):
        r.erro(f"o roteiro tem {len(b)} cabeçalhos de cena e o plano tem "
               f"{len(narradas)} cenas narradas. A cauda NÃO leva cabeçalho no "
               f"roteiro — o s2_tts sintetiza todo bloco e falaria "
               f"'sem narração' em voz alta")
    else:
        r.ok(f"roteiro e plano casam: {len(b)} cenas narradas + "
             f"{len(cenas)-len(narradas)} de cauda")
        titulos_r = [t for _, t, _ in b]
        titulos_p = [c["titulo"] for c in narradas]
        if titulos_r != titulos_p:
            dif = [i+1 for i, (x, y) in enumerate(zip(titulos_r, titulos_p)) if x != y]
            r.erro(f"títulos divergem nas cenas {dif[:6]}")

    # ---- voz
    voz = plano.get("voz") or {}
    try:
        speed = float(voz.get("speed") or 0)
    except (TypeError, ValueError):
        speed = 0.0
    if speed <= 0:
        r.erro("plano sem `voz.speed` — sem ele não dá para projetar duração")
    elif speed < PISO_SPEED:
        r.erro(f"speed {speed} está abaixo do piso {PISO_SPEED}. Medido em "
               f"04/09/2026: abaixo dele o pico de F0 deixa de cair na sílaba "
               f"tônica e toda palavra soa acentuada na primeira. A lentidão "
               f"vem de voz.pausa_respiro_s / voz.pausa_paragrafo_s")
    else:
        r.ok(f"voz {voz.get('voice')} speed {speed} (piso {PISO_SPEED})")

    # ---- duração projetada
    palavras = sum(len(c.split()) for _, _, c in b)
    ppm = _ppm(speed) if speed > 0 else 0
    fala = palavras / ppm if ppm > 0 else 0
    cauda = plano.get("cauda_ambiente_s", 0) / 60
    total = fala + cauda
    alvo = plano.get("duracao_alvo_s", 0) / 60
    if ppm > 0:
        r.ok(f"{palavras:,} palavras / {ppm:.0f} ppm = {fala:.0f} min de fala "
             f"+ {cauda:.0f} de cauda = {total:.0f} min")
    if ppm > 0 and alvo and abs(total - alvo) > alvo * 0.15:
        r.aviso(f"projeção {total:.0f} min contra duracao_alvo_s de {alvo:.0f} "
                f"min — mais de 15% de diferença")
    if ppm > 0 and total < FAIXA_MERCADO[0]:
        r.aviso(f"{total:.0f} min fica abaixo do piso de {FAIXA_MERCADO[0]} que "
                f"docs/mercado.md §2 encontrou. Duração se compra com TEXTO; a "
                f"pausa tem retorno decrescente")

    # ---- estilo
    estilo = (plano.get("estilo_base") or "").strip()
    if not estilo:
        r.erro("plano sem estilo_base — as cenas sairiam com estilos diferentes")
    else:
        maus = [m for p, m, _ in CUES_RUINS if re.search(p, estilo, re.I)]
        for m in maus:
            r.erro(f"estilo_base: {m}")
        if not maus:
            r.ok("estilo_base sem cue conhecidamente ruim")

    obra = (plano.get("obra") or "").strip()
    if not obra:
        r.erro("plano sem obra — é o contexto que segura o traço do personagem")
    elif (ac := [c for c in obra if c.isalpha() and ord(c) > 127]):
        # AVISO e não ERRO: a criação de projeto já barra isso na porta de
        # entrada, e existe título estrangeiro legítimo com acento
        # ("Les Misérables"). Travar a produção inteira por isso seria caro.
        r.aviso(f"obra tem letra acentuada ({''.join(sorted(set(ac)))}), sinal "
                f"de que está em português — o modelo desenharia o título como "
                f"texto ilegível. Se for título estrangeiro de verdade, ignore")
    else:
        r.ok("obra em ASCII, sem negação aparente")

    # ---- cenas
    sem_prompt = [c["n"] for c in narradas if not (c.get("prompt") or "").strip()]
    # `ambiente` é um DICIONÁRIO de níveis (mar/chuva/fogo/vento/abafado), não
    # texto. String ali derruba o s5_render com AttributeError em `cfg.get`.
    tipo_errado = [c["n"] for c in cenas if c.get("ambiente") is not None
                   and not isinstance(c["ambiente"], dict)]
    sem_amb = [c["n"] for c in cenas
               if isinstance(c.get("ambiente"), dict)
               and not any(c["ambiente"].get(k, 0) for k in ("mar", "chuva", "fogo", "vento"))]
    if sem_prompt:
        r.erro(f"cenas sem prompt de imagem: {sem_prompt}")
    else:
        r.ok(f"as {len(narradas)} cenas têm prompt")
    if tipo_errado:
        r.erro(f"cenas com `ambiente` que não é dicionário: {tipo_errado}. O "
               f"s5_render faz cfg.get('mar') e quebra com string. O formato é "
               f"{{mar, chuva, fogo, vento, abafado, _}}")
    if sem_amb:
        r.aviso(f"cenas com ambiente todo em zero (vão sair em silêncio): {sem_amb}")
    if not tipo_errado and not sem_amb:
        r.ok("toda cena tem perfil de ambiente com pelo menos uma camada")

    # \b em "light": sem ele, "flight", "slight" e "delight" davam match e
    # aprovavam a cena por engano.
    LUZ = re.compile(r"\b(night|dark\w*|lantern|lamp\w*|firelight|flame|glow\w*|"
                     r"torch|starlight|dawn|morning|daylight|dusk|light|moon\w*|"
                     r"lit|sun\w*|shadow\w*)\b", re.I)
    sem_luz = [c["n"] for c in narradas if c.get("prompt") and not LUZ.search(c["prompt"])]

    # Os cues UNIVERSais valem no prompt da cena também — foi o buraco que a
    # auditoria achou: o estilo_base passava limpo e uma cena com "no text"
    # gastava dinheiro do mesmo jeito.
    maus_cena = []
    for c in narradas:
        for padrao, motivo, so_base in CUES_RUINS:
            if not so_base and c.get("prompt") and re.search(padrao, c["prompt"], re.I):
                maus_cena.append((c["n"], motivo))
    for n, motivo in maus_cena[:8]:
        r.erro(f"cena {n}: {motivo}")
    if not maus_cena:
        r.ok("nenhum prompt de cena com cue proibido")

    if sem_luz:
        r.aviso(f"cenas cujo prompt não diz a luz: {sem_luz}. O estilo_base não "
                f"fixa hora do dia de propósito, então a cena precisa dizer")
    else:
        r.ok("toda cena traz a própria luz no prompt")

    # ---- custo
    res = plano.get("resolucao") or [1280, 720]
    mp = res[0] * res[1] / 1_000_000
    n_img = len(narradas) + 3
    usd = n_img * mp * USD_POR_MP
    r.ok(f"{n_img} imagens a {res[0]}x{res[1]} = US$ {usd:.2f} "
         f"(R$ {usd*BRL_POR_USD:.2f}); com retentativa 2,5x, "
         f"R$ {usd*BRL_POR_USD*2.5:.2f}")
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="Confere o projeto antes de produzir.")
    ap.add_argument("projeto")
    a = ap.parse_args()
    proj = projeto(a.projeto)
    print(f"\n  {proj.name}\n")
    r = conferir(proj)
    r.imprimir()
    print()
    if r.erros:
        print(f"  {r.erros} erro(s) — corrija antes de produzir\n")
        raise SystemExit(1)
    print("  pronto para produzir\n")


if __name__ == "__main__":
    main()
