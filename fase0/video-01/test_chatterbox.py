import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

model = ChatterboxMultilingualTTS.from_pretrained(device="mps")

texto = """Você chega em casa quando a chuva já começou. Não uma chuva forte,
apenas um som constante batendo no telhado, um sussurro contínuo que preenche
o ar frio da noite."""

wav = model.generate(texto, language_id="pt")
ta.save("teste_chatterbox_base.wav", wav, model.sr)
print("OK — teste_chatterbox_base.wav gerado")
