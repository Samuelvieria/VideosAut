import torchaudio as ta
from functools import lru_cache
import chatterbox.models.s3gen.s3gen as s3gen_module

# Bug do torchaudio.Resample + conv1d no backend MPS ("Output channels > 65536").
# Força esse resample específico a rodar em CPU; o resto do modelo continua em MPS.
@lru_cache(100)
def _cpu_safe_get_resampler(src_sr, dst_sr, device):
    resampler = ta.transforms.Resample(src_sr, dst_sr)

    def wrapped(wav):
        orig_device = wav.device
        return resampler(wav.to("cpu")).to(orig_device)

    return wrapped

s3gen_module.get_resampler = _cpu_safe_get_resampler

from chatterbox.mtl_tts import ChatterboxMultilingualTTS

model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")

texto = """Você chega em casa quando a chuva já começou. Não uma chuva forte,
apenas um som constante batendo no telhado, um sussurro contínuo que preenche
o ar frio da noite."""

wav = model.generate(
    texto,
    language_id="pt",
    audio_prompt_path="vovo_16k.wav",
)
ta.save("teste_clone_vovo.wav", wav, model.sr)
print("OK — teste_clone_vovo.wav gerado")
