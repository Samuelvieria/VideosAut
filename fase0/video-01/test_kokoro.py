import soundfile as sf
from kokoro import KPipeline

pipeline = KPipeline(lang_code="p")  # p = português brasileiro

texto = """Você chega em casa quando a chuva já começou. Não uma chuva forte,
apenas um som constante batendo no telhado, um sussurro contínuo que preenche
o ar frio da noite. A porta se fecha atrás de você com um clique suave, e o
barulho da rua desaparece por completo."""

voice = "pf_dora"  # voz feminina pt-BR

audio_chunks = []
for _, _, audio in pipeline(texto, voice=voice):
    audio_chunks.append(audio)

import numpy as np
full_audio = np.concatenate(audio_chunks)
sf.write("teste_voz.wav", full_audio, 24000)
print("OK — gerado teste_voz.wav")
