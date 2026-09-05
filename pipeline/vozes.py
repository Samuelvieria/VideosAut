"""Gera amostras de voz de vários motores para comparação de ouvido.

    python -m pipeline.vozes --listar
    python -m pipeline.vozes --google-masculinas      # folha de contato
    python -m pipeline.vozes --google Charon,Puck --kokoro --cega

Existe porque as levas anteriores de comparação foram todas feitas à mão, cada
uma com um script descartável. O que não pode ser descartável é o **nivelamento
de loudness**: na rodada contra o Chatterbox ele saiu 10 dB mais alto que o
Kokoro, e sem normalizar a conclusão teria sido "o Chatterbox é melhor" quando
ele só estava mais alto. Aqui isso é obrigatório e automático.

O texto de teste é da cena 2 do video-03 de propósito: contém `manhã` e `água`,
as duas palavras que o Samuel apontou como erradas no Kokoro. A pergunta não é
"qual voz é mais bonita", é **"qual acerta o defeito que eu ouvi"**.
"""
from __future__ import annotations
import argparse
import os
import re
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import log

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "fase0" / "_vozes-candidatas"
LUFS_COMPARACAO = -18.0     # nível único para todas as amostras

# Cena 2 do video-03. Curto de propósito: 16 vozes numa sentada só se ouvem.
TEXTO = (
    "A ilha era pequena. Numa manhã, você atravessava ela de ponta a ponta. "
    "Andando devagar. "
    "Do outro lado da rocha, a baía se abria. Funda e quieta. "
    "Como uma tigela de água escura, esperando os navios que vinham de noite."
)


def _ff(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
                          capture_output=True, text=True)


def nivelar(entrada: Path, saida: Path, alvo: float = LUFS_COMPARACAO) -> None:
    """Normaliza para um LUFS único. Sem isto, comparação de voz não vale nada."""
    _ff(["-i", str(entrada), "-af", f"loudnorm=I={alvo}:TP=-1.5:LRA=7",
         "-ar", "24000", "-ac", "1", str(saida)])


PAUSA_FRASE_PRODUCAO = 1.2      # igual ao plano do video-03


def _com_pausas(sintetizar, texto: str, pausa: float = PAUSA_FRASE_PRODUCAO):
    """Aplica a MESMA estrutura de pausa da produção a qualquer motor.

    Sem isto a comparação é desonesta. O Kokoro sai a 102 ppm porque leva 1,2 s
    de silêncio entre frases; um motor sem pausa nenhuma sai a 170. Posto lado a
    lado, o que se julga passa a ser o ritmo — que é PARÂMETRO nosso, igual para
    todos — em vez do que está em disputa, que é a voz. É a mesma armadilha de
    medir o correlato em vez da coisa (docs/verificacao.md, modo de falha 6).
    """
    import numpy as np
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]
    partes = []
    for i, frase in enumerate(frases):
        partes.append(sintetizar(frase))
        if i < len(frases) - 1:
            partes.append(np.zeros(int(24000 * pausa), dtype=partes[-1].dtype))
    return np.concatenate(partes)


def google_audio(texto: str, voz: str, lang: str = "pt-BR", markup: bool = False):
    """Chirp3-HD, a geração de 2025.

    `markup=True` manda o texto pelo campo `markup` em vez de `text`, que é o
    que habilita as marcas `[pause]`, `[pause short]` e `[pause long]`. A pausa
    nativa é melhor que silêncio costurado por fora: o modelo PLANEJA a
    prosódia em volta dela — a frase anterior fecha a entoação e a seguinte
    reabre —, enquanto silêncio inserido é um corte no meio de uma leitura
    contínua. A mesma voz existe em en-US, en-GB, en-AU e en-IN com o mesmo
    nome, então o narrador não muda de identidade ao trocar de idioma.
    """
    import io, soundfile as sf
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
                          str(Path.home() / ".config" / "gcloud-tts.json"))
    from google.cloud import texttospeech as tts
    cli = tts.TextToSpeechClient()
    entrada = (tts.SynthesisInput(markup=texto) if markup
               else tts.SynthesisInput(text=texto))
    r = cli.synthesize_speech(
        input=entrada,
        voice=tts.VoiceSelectionParams(language_code=lang,
                                       name=f"{lang}-Chirp3-HD-{voz}"),
        audio_config=tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16,
                                     sample_rate_hertz=24000))
    audio, _ = sf.read(io.BytesIO(r.audio_content), dtype="float32")
    return audio if audio.ndim == 1 else audio.mean(axis=1)


# Tratamentos de espaçamento entre frases, para julgar de ouvido. O 1,2 s da
# última linha é o do video-03 — e ele foi calibrado para o KOKORO, que não faz
# pausa nenhuma sozinho. O Samuel ouviu as Chirp3-HD com esse mesmo 1,2 s e
# disse que "o espaçamento está grande": faz sentido, é compensação de um
# motor sendo aplicada a outro que não precisa dela.
TRATAMENTOS = {
    "1_sem_nada":      ("nada — só a pontuação, o modelo decide", None),
    "2_pause_short":   ("marca [pause short] entre frases", "[pause short]"),
    "3_pause":         ("marca [pause] entre frases", "[pause]"),
    "4_pause_long":    ("marca [pause long] entre frases", "[pause long]"),
    "5_pause_duplo":   ("duas marcas [pause] seguidas", "[pause] [pause]"),
    "6_silencio_1s2":  ("1,2 s de silêncio inserido — como está hoje", 1.2),
}


def google(texto: str, voz: str, saida: Path, lang: str = "pt-BR",
           tratamento: str = "3_pause") -> None:
    """Gera uma amostra aplicando um dos tratamentos de espaçamento."""
    import numpy as np, soundfile as sf
    _, modo = TRATAMENTOS[tratamento]
    if modo is None:
        audio = google_audio(texto, voz, lang)
    elif isinstance(modo, str):
        frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]
        audio = google_audio(f" {modo} ".join(frases), voz, lang, markup=True)
    else:
        audio = _com_pausas(lambda t: google_audio(t, voz, lang), texto, modo)
    sf.write(saida, audio, 24000)


def kokoro(texto: str, saida: Path, voz: str = "pm_santa", speed: float = 0.75) -> None:
    """A voz atual, como linha de base — mesma configuração B do video-03.

    Espelha o bloco `voz` do plano do video-03 nos globais do `s2_tts`. Comparar
    contra o Kokoro de fábrica seria comparar contra algo que não está em
    produção: sem a pausa de frase e sem a vogal final corrigida, a linha de
    base sairia pior do que o vídeo publicado, e a comparação favoreceria
    qualquer candidato por um motivo falso.
    """
    import soundfile as sf
    from kokoro import KPipeline
    from pipeline import s2_tts
    s2_tts.PAUSA_RESPIRO, s2_tts.PAUSA_PARAGRAFO = 0.45, 0.30
    s2_tts.PAUSA_FRASE, s2_tts.VOGAL_FINAL_PT = 1.2, True
    pl = KPipeline(lang_code="p")
    sf.write(saida, s2_tts.sintetiza(pl, texto, voz, speed), s2_tts.SR)


def listar_google() -> dict[str, list[str]]:
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
                          str(Path.home() / ".config" / "gcloud-tts.json"))
    from google.cloud import texttospeech as tts
    fora: dict[str, list[str]] = {"MALE": [], "FEMALE": []}
    for v in tts.TextToSpeechClient().list_voices(language_code="pt-BR").voices:
        if "Chirp3-HD" in v.name:
            fora[v.ssml_gender.name].append(v.name.split("Chirp3-HD-")[1])
    return {k: sorted(v) for k, v in fora.items()}


def folha_contato(arquivos: list[tuple[str, Path]], saida: Path) -> None:
    """Junta tudo num wav só, com o número falado antes de cada amostra.

    Ouvir 16 arquivos separados no celular é o tipo de atrito que faz o teste
    não acontecer. O anúncio é sintetizado na voz ATUAL, que é justamente a que
    está sendo comparada — fica óbvio quem é locutor e quem é candidato.
    """
    import numpy as np, soundfile as sf
    from kokoro import KPipeline
    from pipeline import s2_tts
    from pipeline.s2_tts import sintetiza, SR
    s2_tts.PAUSA_FRASE = 0.0        # o locutor não precisa da pausa longa
    pl = KPipeline(lang_code="p")
    silencio = np.zeros(int(SR * 1.0), dtype="float32")
    pedacos = []
    for i, (rotulo, wav) in enumerate(arquivos, 1):
        pedacos.append(sintetiza(pl, f"Número {i}.", "pm_santa", 0.85))
        pedacos.append(np.zeros(int(SR * 0.6), dtype="float32"))
        audio, sr = sf.read(wav, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        pedacos.append(audio)
        pedacos.append(silencio)
        log(f"  {i:2d}. {rotulo}")
    sf.write(saida, np.concatenate(pedacos), SR)


def main() -> None:
    ap = argparse.ArgumentParser(description="Amostras de voz para prova de ouvido.")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--google", help="nomes Chirp3-HD separados por vírgula")
    ap.add_argument("--google-masculinas", action="store_true",
                    help="todas as 16 masculinas, em folha de contato")
    ap.add_argument("--google-femininas", action="store_true")
    ap.add_argument("--kokoro", action="store_true", help="inclui a voz atual")
    ap.add_argument("--cega", action="store_true",
                    help="renomeia para A/B/C... e guarda a correspondência em chave.txt")
    ap.add_argument("--pausas", help="UMA voz; gera os 4 tratamentos de espaçamento")
    ap.add_argument("--lang", default="pt-BR", help="pt-BR, en-US, en-GB…")
    ap.add_argument("--texto", help="sobrescreve o trecho de teste")
    ap.add_argument("--tratamento", default="3_pause", choices=list(TRATAMENTOS))
    ap.add_argument("--saida", default="google-chirp3")
    a = ap.parse_args()

    texto = a.texto or TEXTO

    if a.pausas:
        dest = DESTINO / (a.saida if a.saida != "google-chirp3" else "espacamento")
        dest.mkdir(parents=True, exist_ok=True)
        bruto = dest / "_bruto"; bruto.mkdir(exist_ok=True)
        feitos = []
        for nome, (desc, _) in TRATAMENTOS.items():
            cru, limpo = bruto / f"{nome}.wav", dest / f"{nome}.wav"
            google(texto, a.pausas, cru, a.lang, nome)
            nivelar(cru, limpo)
            feitos.append((f"{nome} — {desc}", limpo))
            log(f"{a.pausas}: {desc}")
        folha_contato(feitos, dest / "contato.wav")
        print(f"\nOK — 4 tratamentos de {a.pausas} em {dest}")
        return

    if a.listar:
        for g, ns in listar_google().items():
            print(f"\n  {g} ({len(ns)}):\n    {', '.join(ns)}")
        return

    dest = DESTINO / a.saida
    dest.mkdir(parents=True, exist_ok=True)
    bruto = dest / "_bruto"
    bruto.mkdir(exist_ok=True)

    vozes = []
    if a.google_masculinas:
        vozes = [("google", v) for v in listar_google()["MALE"]]
    elif a.google_femininas:
        vozes = [("google", v) for v in listar_google()["FEMALE"]]
    elif a.google:
        vozes = [("google", v.strip()) for v in a.google.split(",")]
    if a.kokoro:
        vozes.append(("kokoro", "pm_santa-0.75"))
    if not vozes:
        ap.error("escolha ao menos um motor")

    feitos: list[tuple[str, Path]] = []
    for motor, voz in vozes:
        cru, limpo = bruto / f"{motor}-{voz}.wav", dest / f"{motor}-{voz}.wav"
        # Amostra já gerada não se refaz: as dos motores pagos custam dinheiro,
        # e as locais custam minutos de CPU. Apagar o .wav é o jeito de forçar.
        if limpo.is_file():
            feitos.append((f"{motor}/{voz}", limpo))
            log(f"já existe {motor}/{voz}")
            continue
        if motor == "google":
            google(texto, voz, cru, a.lang, a.tratamento)
        else:
            kokoro(texto, cru)
        nivelar(cru, limpo)
        feitos.append((f"{motor}/{voz}", limpo))
        log(f"gerada {motor}/{voz}")

    if a.cega:
        random.shuffle(feitos)
        chave = []
        for i, (rotulo, wav) in enumerate(feitos):
            letra = chr(ord("A") + i)
            novo = dest / f"{letra}.wav"
            wav.rename(novo)
            chave.append(f"{letra} = {rotulo}")
            feitos[i] = (letra, novo)
        (dest / "chave.txt").write_text("\n".join(chave) + "\n", encoding="utf-8")
        log("chave.txt escrito — NÃO abrir antes de ouvir")

    folha_contato(feitos, dest / "contato.wav")
    print(f"\nOK — {len(feitos)} amostras em {dest}")
    print(f"     folha de contato: {dest / 'contato.wav'}")
    print(f"     nivelado a {LUFS_COMPARACAO} LUFS; ouça no fone, à noite, no volume de dormir")


if __name__ == "__main__":
    main()
