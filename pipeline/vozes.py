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


def google(texto: str, voz: str, saida: Path) -> None:
    """Chirp3-HD, a geração de 2025. Fala em ritmo natural — a lentidão do
    formato vem da pausa entre frases, não de esticar a fala (ver a skill)."""
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
                          str(Path.home() / ".config" / "gcloud-tts.json"))
    from google.cloud import texttospeech as tts
    cli = tts.TextToSpeechClient()
    r = cli.synthesize_speech(
        input=tts.SynthesisInput(text=texto),
        voice=tts.VoiceSelectionParams(language_code="pt-BR",
                                       name=f"pt-BR-Chirp3-HD-{voz}"),
        audio_config=tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16,
                                     sample_rate_hertz=24000))
    saida.write_bytes(r.audio_content)


def kokoro(texto: str, saida: Path, voz: str = "pm_santa", speed: float = 0.75) -> None:
    """A voz atual, como linha de base — mesma configuração B do video-03."""
    import numpy as np, soundfile as sf
    from kokoro import KPipeline
    from pipeline.s2_tts import sintetiza, SR
    pl = KPipeline(lang_code="p")
    sf.write(saida, np.concatenate(sintetiza(pl, texto, voz, speed)), SR)


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
    from pipeline.s2_tts import sintetiza, SR
    pl = KPipeline(lang_code="p")
    silencio = np.zeros(int(SR * 1.0), dtype="float32")
    pedacos = []
    for i, (rotulo, wav) in enumerate(arquivos, 1):
        pedacos.append(np.concatenate(sintetiza(pl, f"Número {i}.", "pm_santa", 0.85)))
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
    ap.add_argument("--saida", default="google-chirp3")
    a = ap.parse_args()

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
        if motor == "google":
            google(TEXTO, voz, cru)
        else:
            kokoro(TEXTO, cru)
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
