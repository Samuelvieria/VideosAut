"""Coletor de lixo: libera espaço depois que um vídeo fica pronto.

    python -m pipeline.limpar fase0/video-03           # SÓ MOSTRA (padrão)
    python -m pipeline.limpar fase0/video-03 --apagar
    python -m pipeline.limpar --todos                  # varre fase0/ inteiro
    python -m pipeline.limpar --todos --apagar

Padrão é seco. Apagar exige `--apagar` escrito à mão — ferramenta destrutiva não
deve ter caminho curto.

## A regra que organiza tudo

Cada arquivo cai numa de três faixas, e a pergunta é sempre a mesma: **quanto
custa recriar isto?**

| faixa | o que é | critério |
|---|---|---|
| descartável | `build/`, `*.stamp` órfão | segundos ou minutos de CPU, e nada mais |
| condicional | `audio/`, `final.mp4` | grátis mas lento; só sai se o vídeo já foi publicado |
| **intocável** | `imagens/`, `thumbnails/` | **custou dinheiro** e foi aprovado de olho |

As imagens do video-03 custaram R$ 1,97 e o Samuel disse "não é pra mexer
nelas". Nenhuma flag deste módulo as apaga — nem `--apagar`, nem `--todos`. Se
um dia for preciso, é `rm` na mão, com a pessoa olhando.

## Por que `final.mp4` é condicional e não descartável

Ele é o entregável. Enquanto o vídeo não está no YouTube, é a única cópia do
trabalho. Depois de publicado, o YouTube é o backup — e refazer custa só tempo
de máquina, porque tudo que o alimenta (roteiro, plano, imagens) está guardado.

O módulo detecta publicação por `publicacao.video_id` no `plano.json`. Sem esse
campo, ele assume NÃO publicado e preserva.
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import log

RAIZ = Path(__file__).resolve().parent.parent
FASE0 = RAIZ / "fase0"

# Nunca, sob nenhuma flag. Custaram dinheiro ou foram aprovadas de olho.
INTOCAVEIS = ("imagens", "thumbnails")


def _mb(p: Path) -> float:
    if p.is_file():
        return p.stat().st_size / 1_048_576
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1_048_576


def _publicado(proj: Path) -> str | None:
    """Devolve o video_id se o plano registra publicação; senão None."""
    try:
        plano = json.loads((proj / "plano.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    return ((plano.get("publicacao") or {}).get("video_id")) or None


def _stamps_orfaos(proj: Path) -> list[Path]:
    """`.stamp` cujo arquivo correspondente não existe mais.

    Aparecem quando alguém apaga um `.wav` ou `.png` na mão e esquece a marca.
    A marca sozinha não faz mal, mas mente sobre o estado do projeto — e este
    projeto já perdeu tempo por causa de marca que não correspondia à realidade.
    """
    return [s for s in proj.rglob("*.stamp")
            if not s.with_suffix("").exists()]


def analisar(proj: Path) -> list[tuple[Path, float, str, bool]]:
    """(caminho, MB, motivo, pode_apagar) para cada candidato."""
    itens: list[tuple[Path, float, str, bool]] = []
    vid = _publicado(proj)

    build = proj / "build"
    if build.is_dir():
        itens.append((build, _mb(build),
                      "intermediários do render; o concat final já os consumiu", True))

    final = proj / "final.mp4"
    if final.is_file():
        if vid:
            itens.append((final, _mb(final),
                          f"publicado como {vid} — o YouTube é o backup", True))
        else:
            itens.append((final, _mb(final),
                          "NÃO publicado — é a única cópia do entregável", False))

    audio = proj / "audio"
    if audio.is_dir():
        wavs = list(audio.glob("cena_*.wav"))
        # Áudio PARCIAL é lixo mesmo em projeto não publicado: uma geração
        # interrompida deixa metade das cenas, e o s2_tts nem consegue seguir
        # dali — o s5_render aborta com "faltam áudios". Guardar isso não
        # protege nada e ainda mente sobre o estado do projeto.
        try:
            esperadas = len([c for c in json.loads(
                (proj / "plano.json").read_text(encoding="utf-8"))["cenas"]
                if c.get("papel") != "cauda-ambiente"])
        except Exception:
            esperadas = 0
        if esperadas and 0 < len(wavs) < esperadas:
            itens.append((audio, _mb(audio),
                          f"PARCIAL: {len(wavs)} de {esperadas} cenas — geração "
                          f"interrompida, inutilizável como está", True))
        elif vid:
            itens.append((audio, _mb(audio),
                          f"{len(wavs)} cenas; regenerável pelo s2_tts, e o vídeo já saiu", True))
        else:
            itens.append((audio, _mb(audio),
                          f"{len(wavs)} cenas; regenerável, mas o vídeo ainda não saiu", False))

    orfaos = _stamps_orfaos(proj)
    if orfaos:
        tot = sum(s.stat().st_size for s in orfaos) / 1_048_576
        itens.append((proj, tot, f"{len(orfaos)} marca(s) órfã(s), sem o arquivo correspondente", True))

    for nome in INTOCAVEIS:
        d = proj / nome
        if d.is_dir():
            itens.append((d, _mb(d), "INTOCÁVEL — custou dinheiro ou foi aprovado de olho", False))
    return itens


def limpar(proj: Path, apagar: bool) -> float:
    vid = _publicado(proj)
    estado = f"publicado ({vid})" if vid else "não publicado"
    print(f"\n  {proj.name}  ·  {estado}")
    itens = analisar(proj)
    if not itens:
        print("    nada a analisar")
        return 0.0

    liberado = 0.0
    for caminho, mb, motivo, pode in sorted(itens, key=lambda x: -x[1]):
        nome = caminho.name if caminho != proj else "(marcas órfãs)"
        if pode:
            liberado += mb
            marca = "APAGA " if apagar else "apagaria"
        else:
            marca = "mantém"
        print(f"    {marca} {mb:8.1f} MB  {nome:<14} {motivo}")

    if apagar:
        for caminho, _, _, pode in itens:
            if not pode:
                continue
            if caminho == proj:                       # marcas órfãs
                for s in _stamps_orfaos(proj):
                    s.unlink()
            elif caminho.is_dir():
                shutil.rmtree(caminho)
            else:
                caminho.unlink()
    return liberado


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Libera espaço de projetos já montados. Seco por padrão.")
    ap.add_argument("projeto", nargs="?", help="fase0/video-NN; omita com --todos")
    ap.add_argument("--todos", action="store_true", help="varre fase0/ inteiro")
    ap.add_argument("--apagar", action="store_true",
                    help="executa de verdade; sem isto, só mostra")
    a = ap.parse_args()

    if a.todos:
        projs = sorted(d for d in FASE0.iterdir()
                       if d.is_dir() and (d / "plano.json").is_file())
    elif a.projeto:
        p = Path(a.projeto)
        p = p if p.is_absolute() else RAIZ / p
        if not (p / "plano.json").is_file():
            raise SystemExit(f"não é um projeto: {p}")
        projs = [p]
    else:
        ap.error("informe um projeto ou use --todos")

    total = sum(limpar(p, a.apagar) for p in projs)
    print()
    if a.apagar:
        log(f"liberados {total:.0f} MB ({total/1024:.1f} GB)")
    else:
        log(f"liberaria {total:.0f} MB ({total/1024:.1f} GB) — rode com --apagar")
    print("\n  As imagens e thumbnails nunca são apagadas por este módulo.")
    print("  Elas custaram dinheiro; se precisar mesmo, é rm na mão.\n")


if __name__ == "__main__":
    main()
