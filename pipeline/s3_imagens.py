#!/usr/bin/env python3
"""s3 — gera as imagens de cena via fal.ai (Z-Image-Turbo).

    python -m pipeline.s3_imagens fase0/video-02 [--cena N] [--forcar] [--seco]

Gera em 768x432 — 640x360 (a densidade de pixel real, ×3 até 1920x1080 no
s5_render) mais 128x72 de MARGEM pro corte deslizante do movimento de cena
(ver PAN_* em pipeline/s5_render.py). O s5_render sempre recorta uma janela de
640x360 desse arquivo (parada e centralizada, ou deslizando pela margem) antes
de escalar ×3 com `flags=neighbor` — nunca a imagem inteira direto, e nunca
escala fracionária: pixel art interpolado perde a grade e o estilo morre.
Ver docs/imagens-provedores.md e fase0/video-02/estilo.yaml.

O prompt final é obra + personagem + cena (contexto narrativo) seguido de
`estilo_base` + o prompt visual da cena. Medido em 27/08/2026: sem o contexto
narrativo na frente, o modelo perde o traço que define o personagem quando ele
compete com o resto da descrição (a perna de marfim do Ahab sumiu duas vezes
seguidas até o prompt passar a abrir com "Captain Ahab" antes da descrição
física). `obra` e `personagem` vêm do plano.json; cena sem personagem nomeado
usa "no character — ...".

O Z-Image-Turbo NÃO aceita `negative_prompt`, então os negativos do estilo.yaml
não têm para onde ir — o que dá para fazer é manter o estilo_base explícito o
bastante para não abrir espaço a eles. Se aparecer texto ou elemento moderno
nas imagens, é aqui que está a causa.
"""
from __future__ import annotations
import argparse, json, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import atualizado, carregar_plano, erro, log, marcar, projeto
from pipeline.config import obter

MODELO = "fal-ai/z-image/turbo"

# MEDIDO 02/09/2026: a fal.ai NAO honra dimensao abaixo de 512 — ela empurra
# para 512 sem avisar, e a resposta vem com o tamanho real (nao o pedido).
#   pedido 640x360 -> devolveu 640x512   (razao 1.25, nao 16:9)
#   pedido 768x432 -> devolveu 768x512   (razao 1.50, nao 16:9)
#   pedido 1024x576 -> devolveu 1024x576  OK
# Por isso 1024x576: e o preset landscape_16_9 do proprio modelo. Qualquer
# alteracao aqui precisa manter as DUAS dimensoes >= 512, senao a imagem sai
# com outra proporcao e o corte do s5_render passa a comer composicao.
LARG, ALT = 1280, 720   # margem de pan; ver PAN_* no s5_render
PASSOS = 8


def _post(url: str, corpo: dict, chave: str) -> dict:
    """POST na fal.ai. A doc mostra `Bearer`; instalações antigas usam `Key`.
    Tenta os dois em vez de falhar por um detalhe de cabeçalho."""
    ultimo = None
    for esquema in ("Key", "Bearer"):
        req = urllib.request.Request(
            url, data=json.dumps(corpo).encode(),
            headers={"Authorization": f"{esquema} {chave}",
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            ultimo = (esquema, e.code, e.read().decode()[:300])
            if e.code not in (401, 403):
                break
    erro(f"fal.ai recusou ({ultimo[0]} → HTTP {ultimo[1]}):\n{ultimo[2]}")


def gerar(prompt: str, seed: int, chave: str) -> bytes:
    r = _post(f"https://fal.run/{MODELO}", {
        "prompt": prompt,
        "image_size": {"width": LARG, "height": ALT},
        "num_inference_steps": PASSOS,
        "num_images": 1,
        "seed": seed,
        "output_format": "png",
        # O provedor tem um LLM interno que reescreve o prompt antes de gerar.
        # Ligado, ele injeta adjetivos diferentes a cada chamada — o que sabota
        # por baixo dos panos a consistência de estilo que a seed fixa e o
        # prefixo tentam garantir. Desligado, o prompt chega como escrevemos.
        "enable_prompt_expansion": False,
    }, chave)
    imgs = r.get("images") or []
    if not imgs:
        erro(f"resposta sem imagem: {json.dumps(r)[:300]}")
    with urllib.request.urlopen(imgs[0]["url"], timeout=120) as f:
        return f.read()


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera as imagens de cena.")
    ap.add_argument("projeto")
    ap.add_argument("--cena", type=int, help="gera só esta cena (para testar)")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--seco", action="store_true", help="monta os prompts e sai, sem gastar")
    a = ap.parse_args()

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    estilo = plano.get("estilo_base", "").strip()
    if not estilo:
        erro("plano.json sem estilo_base — as cenas sairiam com estilos diferentes")
    obra = plano.get("obra", "").strip()

    seed_base = 20260826
    try:
        import yaml
        y = yaml.safe_load((proj / "estilo.yaml").read_text(encoding="utf-8"))
        seed_base = int(y.get("seed", {}).get("base", seed_base))
    except Exception:
        log("estilo.yaml não lido; usando seed base padrão")

    dest = proj / "imagens"; dest.mkdir(exist_ok=True)
    cenas = [c for c in plano["cenas"] if a.cena is None or c["n"] == a.cena]
    if not cenas:
        erro(f"cena {a.cena} não existe no plano")

    chave = None if a.seco else obter("FAL_KEY")
    for c in cenas:
        alvo = dest / f"cena_{c['n']:02d}.png"
        # `seed_de` permite que uma cena reuse a seed de outra. Existe para a
        # moldura (cenas 1 e 19): mesma composição, momento diferente. Sem isso
        # o gerador entrega outro cais e o dispositivo narrativo não fecha.
        seed = seed_base + int(c.get("seed_de", c["n"]))
        # Contexto narrativo ANTES da descrição visual: obra, personagem e a
        # cena da história. Sem isso o modelo perde o traço que define o
        # personagem quando ele compete com o resto da descrição (ver docstring).
        # `contexto_narrativo: false` desliga isso por cena — existe porque
        # medido em 27/08/2026: na cena da baleia branca, nomear "the white
        # whale" no contexto reativa o viés de pose de salto (jubarte) que o
        # prompt visual já tinha sido ajustado para evitar. Contexto genérico
        # pode reforçar clichê de treino tão bem quanto resolver perda de traço.
        contexto = ""
        if c.get("contexto_narrativo", True):
            contexto = ", ".join(x for x in (obra, c.get("personagem", "").strip(),
                                              f"scene: {c['titulo']}") if x)
        prompt = f"{contexto}. {estilo}, {c['prompt']}" if contexto else f"{estilo}, {c['prompt']}"
        cfg = f"{MODELO};{LARG}x{ALT};steps={PASSOS};seed={seed};{prompt[:180]}"

        if a.seco:
            print(f"\n--- cena {c['n']:02d} · seed {seed} · {c['titulo']}")
            print(f"{prompt}")
            continue
        if not a.forcar and atualizado(alvo, [], cfg):
            log(f"cena {c['n']:02d}  já gerada")
            continue

        t = time.time()
        alvo.write_bytes(gerar(prompt, seed, chave))
        marcar(alvo, [], cfg)
        log(f"cena {c['n']:02d}  {time.time()-t:5.1f}s  {alvo.stat().st_size/1024:5.0f} KB  {c['titulo']}")


if __name__ == "__main__":
    main()
