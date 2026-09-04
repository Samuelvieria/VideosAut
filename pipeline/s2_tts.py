#!/usr/bin/env python3
"""s2 — gera um .wav de narração por cena, a partir de roteiro.md.

    python -m pipeline.s2_tts fase0/video-02 [--forcar]

Por cena, e não num arquivo único, porque é a duração real do áudio de cada bloco
que define quanto tempo a imagem daquela cena fica na tela. O áudio manda no corte.

Voz e velocidade vêm do bloco `voz` do plano.json, não ficam fixas aqui — cada
vídeo pode ter uma persona diferente.
"""
from __future__ import annotations
import hashlib
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
PAUSA_FRASE = 0.0         # entre frases DENTRO do parágrafo; 0 = comportamento antigo

# MEDIDO 04/09/2026: o Kokoro pt-BR tem um contorno de fim de frase só. Ponto,
# reticências, vírgula, "?" e "!" dão todos a mesma queda de F0 (-39 a -53 Hz),
# nas três vozes (pm_santa, pm_alex, pf_dora). Não há entonação interrogativa a
# extrair, e a pontuação não dirige nada.
#
# A ÚNICA variação que apareceu: no pm_santa, frase alimentada terminando em
# VÍRGULA cai -19 Hz contra -53 do ponto. Queda mais rasa lê como "continua" em
# vez de "fecha". `CADENCIA_ALTERNADA` usa isso: troca o ponto final por vírgula
# em algumas frases, dando duas cadências em vez de uma. É paliativo — a
# variação de verdade pede outro motor (ver docs/tts-provedores.md).
CADENCIA_ALTERNADA = 0    # de N em N frases, alimenta com vírgula; 0 = desligado

# O espeak-ng mapeia o /a/ átono final do português para `æ` — o mesmo símbolo
# da vogal de "cat" em inglês. Ele faz isso por convenção interna, não por erro.
# O risco é o Kokoro: sendo multilíngue, se o treino da voz pt-BR não ancorou
# esse símbolo com densidade, o modelo o realiza com timbre inglês.
#
# MEDIDO 04/09/2026: trocar æ por ɐ encurta a palavra de 3% (água) a 8% (ponta)
# e sobe o F0 final de 123 para 129 Hz em "água". Efeito pequeno mas na direção
# certa, e ɐ é o símbolo foneticamente correto para pt-BR. Fica opcional porque
# não foi julgado de ouvido ainda, e porque mexer nisso mudaria o video-02.
VOGAL_FINAL_PT = False    # True troca æ por ɐ na saída do fonemizador

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
    n_frase = 0
    for i, par in enumerate([p for p in texto.split("\n\n") if p.strip()]):
        partes = [x.strip() for x in par.split("...") if x.strip()]
        for j, parte in enumerate(partes):
            ult_parte = j == len(partes) - 1
            base_parte = PAUSA_PARAGRAFO if ult_parte else PAUSA_RESPIRO

            # Corte por FRASE. Antes o corte era só nos "..." e nos parágrafos,
            # então um parágrafo de cinco frases ia ao modelo num bloco e não
            # havia pausa nenhuma entre elas — o Samuel ouviu isso e pediu.
            if PAUSA_FRASE > 0:
                frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", parte) if f.strip()]
            else:
                frases = [parte]

            for k, frase in enumerate(frases):
                ult_frase = k == len(frases) - 1
                if CADENCIA_ALTERNADA and not ult_frase and n_frase % CADENCIA_ALTERNADA == 0:
                    frase = re.sub(r"\.$", ",", frase)
                n_frase += 1
                pausa = (base_parte if ult_frase else PAUSA_FRASE) * fator_pausa
                pedacos.append((frase, pausa))
    if pedacos:
        pedacos[-1] = (pedacos[-1][0], 0.0)

    saida = []
    for texto_i, pausa in pedacos:
        # Pedaço sem nenhuma letra não gera áudio, e `np.concatenate([])`
        # levanta ValueError que derrubava o estágio inteiro na cena 38. Pular é
        # o certo: pontuação solta não é fala. A pausa dele é preservada, para o
        # ritmo não mudar por causa do descarte.
        if not re.search(r"[^\W\d_]", texto_i, re.UNICODE):
            if pausa > 0 and saida:
                saida.append(np.zeros(int(SR * pausa), dtype=saida[-1].dtype))
            continue
        pedaco = [a for _, _, a in pipeline(texto_i, voice=voice, speed=speed)]
        if not pedaco:
            log(f"aviso: o modelo não devolveu áudio para {texto_i[:50]!r}; pulado")
            continue
        saida.append(np.concatenate(pedaco))
        if pausa > 0:
            saida.append(np.zeros(int(SR * pausa), dtype=saida[-1].dtype))
    if not saida:
        erro(f"nenhum áudio gerado para o bloco: {texto[:80]!r}")
    return np.concatenate(saida)


def _marca(cfg: str, corpo: str) -> str:
    """Assinatura de uma cena: config + hash do texto DELA.

    Era `[roteiro]` como entrada, ou seja o arquivo inteiro — então mudar uma
    palavra numa cena invalidava as 38 e regerava tudo. E o texto entrava
    truncado em 200 caracteres, o que deixava duas cenas de mesmo começo
    indistinguíveis. Agora é o texto completo da cena, em hash, e nada mais.
    """
    return f"{cfg};texto={hashlib.sha256(corpo.encode()).hexdigest()[:16]}"


def blocos(roteiro: Path) -> list[tuple[int, str, str]]:
    """Extrai (n, titulo, corpo) de cada `## Cena N — Titulo` do roteiro."""
    txt = roteiro.read_text(encoding="utf-8")
    # Comentário HTML é ANOTAÇÃO, não narração. Descoberto em 04/09/2026: a nota
    # que explica por que a cauda não leva cabeçalho fica DEPOIS do último
    # cabeçalho de cena, então entrava no corpo da cena 38 — e a voz teria lido
    # o comentário em voz alta no fecho do vídeo. Mesma família do "(sem
    # narração)" que já tinha sido pego.
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
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

    # A pausa passou a ser parâmetro DO PROJETO em 04/09/2026, não constante
    # global. Motivo: medido que `speed` abaixo de 0.85 destrói o acento tonal
    # (o pico de F0 deixa de cair na sílaba tônica e a curva só decai, e aí toda
    # palavra soa acentuada na primeira sílaba). A lentidão tem que vir da
    # pausa. Mas mexer nas constantes mudaria o video-02, que está publicado —
    # então cada projeto traz as suas, com o valor antigo como padrão.
    global PAUSA_RESPIRO, PAUSA_PARAGRAFO, PAUSA_FRASE, CADENCIA_ALTERNADA
    global VOGAL_FINAL_PT
    PAUSA_RESPIRO = float(voz.get("pausa_respiro_s", PAUSA_RESPIRO))
    PAUSA_PARAGRAFO = float(voz.get("pausa_paragrafo_s", PAUSA_PARAGRAFO))
    PAUSA_FRASE = float(voz.get("pausa_frase_s", PAUSA_FRASE))
    CADENCIA_ALTERNADA = int(voz.get("cadencia_alternada", CADENCIA_ALTERNADA))
    VOGAL_FINAL_PT = bool(voz.get("vogal_final_pt", VOGAL_FINAL_PT))

    roteiro = proj / "roteiro.md"
    if not roteiro.is_file():
        erro(f"falta {roteiro}")

    destino = proj / "audio"
    destino.mkdir(exist_ok=True)
    cfg = (f"voice={voice};speed={speed};respiro={PAUSA_RESPIRO}/{PAUSA_PARAGRAFO};"
           f"frase={PAUSA_FRASE};cadencia={CADENCIA_ALTERNADA};"
           f"vogal_pt={VOGAL_FINAL_PT};"
           f"fator_pausa={FATOR_PAUSA_INICIO}-{FATOR_PAUSA_FIM}")

    cenas = blocos(roteiro)
    total_cenas = len(cenas)
    pendentes = [c for c in cenas
                 if a.forcar or not atualizado(destino / f"cena_{c[0]:02d}.wav", [], _marca(cfg, c[2]))]

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
        if VOGAL_FINAL_PT:
            _g2p = pipeline.g2p

            def _g2p_pt(texto):
                ps, extra = _g2p(texto)
                if isinstance(ps, str):
                    ps = ps.replace("æ", "ɐ")
                return ps, extra
            pipeline.g2p = _g2p_pt
            log("vogal final: æ -> ɐ (VOGAL_FINAL_PT ligado)")
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
            marcar(alvo, [], _marca(cfg, corpo))
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
