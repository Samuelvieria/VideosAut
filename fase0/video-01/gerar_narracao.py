"""Gera a narração completa em áudio a partir de narracao.txt.

Voz final escolhida para este vídeo: pm_santa, speed=0.80, sem pitch shift.
Ver CLAUDE.md (seção TTS) para o porquê dessas escolhas.
"""
import soundfile as sf
import numpy as np
from kokoro import KPipeline

VOICE = "pm_santa"
SPEED = 0.80
SAMPLE_RATE = 24000

pipeline = KPipeline(lang_code="p")

texto = open("narracao.txt", encoding="utf-8").read()

chunks = []
for _, _, audio in pipeline(texto, voice=VOICE, speed=SPEED):
    chunks.append(audio)

full_audio = np.concatenate(chunks)
sf.write("narracao.wav", full_audio, SAMPLE_RATE)

duracao_min = len(full_audio) / SAMPLE_RATE / 60
print(f"OK — narracao.wav gerado ({duracao_min:.1f} min)")
