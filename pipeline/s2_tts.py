#!/usr/bin/env python3
"""s2 — gera um .wav de narração por cena, a partir de roteiro.md.

    python -m pipeline.s2_tts fase0/video-02 [--forcar]

Por cena, e não num arquivo único, porque é a duração real do áudio de cada bloco
que define quanto tempo a imagem daquela cena fica na tela. O áudio manda no corte.

Voz e velocidade vêm do bloco `voz` do plano.json, não ficam fixas aqui — cada
vídeo pode ter uma persona diferente.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import atualizado, carregar_plano, erro, log, marcar, projeto

SR = 24000

# "..." no roteiro é ANOTAÇÃO DE RESPIRAÇÃO, não pontuação para o modelo ler.
# Medido em 27/08/2026: o Kokoro ignora reticências — a cena 4 pontuada saiu com
# MENOS pausa que a original (13 contra 17 pausas, 5,46s contra 6,76s). O conselho
# de "usar reticências" vem do ElevenLabs, que tem SSML; o Kokoro não tem.
# Então cortamos o texto nos "..." e inserimos o silêncio nós mesmos.
PAUSA_RESPIRO = 0.45      # segundos de silêncio em cada "..."
PAUSA_PARAGRAFO = 0.30    # respiro extra entre parágrafos

# Densidade decrescente pela PAUSA, não pela articulação — ver pesquisa de
# ritmo de 28/08/2026 (.claude/skills/qualidade-producao-video/SKILL.md,
# seção "Ritmo de narração"). `speed` do Kokoro estica tudo por igual,
# inclusive consoante, e soa "sedado"; o jeito certo de desacelerar é dar mais
# silêncio entre frases/parágrafos, crescendo ao longo do episódio. FATOR_*
# definem esse crescimento: cena 1 usa 1.0× a pausa base, a última cena do
# corpo narrado usa FATOR_PAUSA_FIM×.
FATOR_PAUSA_INICIO = 1.0
FATOR_PAUSA_FIM = 1.6


def sintetiza(pipeline, texto: str, voice: str, speed: float, fator_pausa: float = 1.0):
    """Sintetiza um bloco honrando as marcas de respiração.

    O texto é cortado nos "..." e em quebras de parágrafo; cada pedaço vai ao
    modelo separadamente e o silêncio entra entre eles. Isso resolve dois
    problemas de uma vez: dá a pausa que o Kokoro não dá sozinho, e alimenta o
    modelo com passagens curtas — que é onde ele erra menos prosódia.

    `fator_pausa` escala PAUSA_RESPIRO/PAUSA_PARAGRAFO pra essa cena — é como
    o chamador implementa densidade decrescente ao longo do episódio sem
    tocar em `speed` (ver FATOR_PAUSA_INICIO/FIM).
    """
    import numpy as np

    pedacos: list[tuple[str, float]] = []
    for i, par in enumerate([p for p in texto.split("\n\n") if p.strip()]):
        partes = [x.strip() for x in par.split("...") if x.strip()]
        for j, parte in enumerate(partes):
            ult = j == len(partes) - 1
            base = PAUSA_PARAGRAFO if ult else PAUSA_RESPIRO
            pedacos.append((parte, base * fator_pausa))
    if pedacos:
        pedacos[-1] = (pedacos[-1][0], 0.0)

    saida = []
    for texto_i, pausa in pedacos:
        saida.append(np.concatenate([a for _, _, a in pipeline(texto_i, voice=voice, speed=speed)]))
        if pausa > 0:
            saida.append(np.zeros(int(SR * pausa), dtype=saida[-1].dtype))
    return np.concatenate(saida)


def blocos(roteiro: Path) -> list[tuple[int, str, str]]:
    """Extrai (n, titulo, corpo) de cada `## Cena N — Titulo` do roteiro."""
    txt = roteiro.read_text(encoding="utf-8")
    partes = re.split(r"^## Cena (\d+) — (.+)$", txt, flags=re.M)[1:]
    if not partes:
        erro(f"{roteiro} não tem nenhum cabeçalho '## Cena N — Título'")
    saida = []
    for i in range(0, len(partes), 3):
        corpo = re.sub(r"\n{3,}", "\n\n", partes[i + 2]).strip()
        saida.append((int(partes[i]), partes[i + 1].strip(), corpo))
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera a narração por cena.")
    ap.add_argument("projeto")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    voz = plano.get("voz", {})
    voice = voz.get("voice", "pm_santa")
    speed = float(voz.get("speed", 0.80))

    roteiro = proj / "roteiro.md"
    if not roteiro.is_file():
        erro(f"falta {roteiro}")

    destino = proj / "audio"
    destino.mkdir(exist_ok=True)
    cfg = (f"voice={voice};speed={speed};respiro={PAUSA_RESPIRO}/{PAUSA_PARAGRAFO};"
           f"fator_pausa={FATOR_PAUSA_INICIO}-{FATOR_PAUSA_FIM}")

    cenas = blocos(roteiro)
    total_cenas = len(cenas)
    pendentes = [c for c in cenas
                 if a.forcar or not atualizado(destino / f"cena_{c[0]:02d}.wav", [roteiro], cfg + c[2][:200])]

    if not pendentes:
        log("todas as cenas já estão atualizadas")
    else:
        # importa só quando há trabalho: carregar o Kokoro custa segundos
        import numpy as np, soundfile as sf

        # Aponta o phonemizer para o espeak-ng empacotado via pip, em vez de
        # depender de instalação no sistema (brew/apt). No Windows não há
        # gerenciador de pacotes padrão para isso; espeakng_loader funciona
        # igual nas três plataformas, então fixamos por aqui sempre.
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())

        from kokoro import KPipeline
        pipeline = KPipeline(lang_code="p")
        log(f"voz={voice} speed={speed} — {len(pendentes)} cena(s) a gerar")
        for n, titulo, corpo in pendentes:
            alvo = destino / f"cena_{n:02d}.wav"
            # posição relativa da cena no episódio (0 na primeira, 1 na
            # última) — cresce a pausa, não a lentidão da fala, ao longo do
            # episódio (densidade decrescente, ver FATOR_PAUSA_*)
            pos = (n - 1) / max(1, total_cenas - 1)
            fator = FATOR_PAUSA_INICIO + (FATOR_PAUSA_FIM - FATOR_PAUSA_INICIO) * pos
            audio = sintetiza(pipeline, corpo, voice, speed, fator)
            sf.write(alvo, audio, SR)
            marcar(alvo, [roteiro], cfg + corpo[:200])
            log(f"cena {n:02d}  {len(audio)/SR:6.1f}s  {titulo}  (pausa×{fator:.2f})")

    # relatório consolidado, consumido pelo s5
    from pipeline.comum import duracao
    linhas = []
    for n, titulo, corpo in cenas:
        w = destino / f"cena_{n:02d}.wav"
        if not w.exists():
            continue
        d = duracao(w)
        linhas.append({"n": n, "titulo": titulo, "dur_s": round(d, 2),
                       "palavras": len(corpo.split()),
                       "ppm": round(len(corpo.split()) / (d / 60))})
    total = sum(l["dur_s"] for l in linhas)
    json.dump({"voice": voice, "speed": speed, "total_s": round(total, 2), "cenas": linhas},
              open(proj / "duracoes.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    alvo_s = float(plano.get("duracao_alvo_s", 1800))
    print(f"\nnarrado: {total/60:.1f} min  |  cauda para fechar {alvo_s/60:.0f} min: "
          f"{(alvo_s-total)/60:.1f} min")
    if linhas:
        print(f"ritmo médio: {sum(l['ppm'] for l in linhas)//len(linhas)} palavras/min")


if __name__ == "__main__":
    main()
