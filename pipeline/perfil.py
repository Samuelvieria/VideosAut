"""Perfil de hardware — o que muda entre a máquina atual e uma workstation.

A ideia é que migrar de máquina seja trocar de perfil, não reescrever estágio.
Tudo que depende de CPU/RAM/GPU mora aqui; nenhum estágio lê hardware direto.

    from pipeline.perfil import perfil
    p = perfil()
    p.whisper_device, p.whisper_compute, p.x264_preset, p.jobs

Override manual (útil para testar o perfil da outra máquina antes de mudar):

    PERFIL=workstation python -m pipeline.s5_render fase0/video-02
    PERFIL=teste       python -m pipeline.s4_legendas fase0/video-02
"""
from __future__ import annotations
import os, subprocess, sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Perfil:
    nome: str
    whisper_modelo: str
    whisper_device: str
    whisper_compute: str
    x264_preset: str
    jobs: int              # clipes renderizados em paralelo
    nota: str = ""

    def __str__(self) -> str:
        return (f"perfil '{self.nome}': whisper={self.whisper_modelo}/"
                f"{self.whisper_device}/{self.whisper_compute}, "
                f"x264={self.x264_preset}, jobs={self.jobs}")


def _ram_gb() -> float:
    try:
        if sys.platform == "darwin":
            n = int(subprocess.run(["sysctl", "-n", "hw.memsize"],
                                   capture_output=True, text=True).stdout.strip())
            return n / 1024 ** 3
        if sys.platform == "win32":
            import ctypes
            class _MEMSTATUS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = _MEMSTATUS(); m.dwLength = ctypes.sizeof(_MEMSTATUS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.ullTotalPhys / 1024 ** 3
        with open("/proc/meminfo") as f:
            for l in f:
                if l.startswith("MemTotal:"):
                    return int(l.split()[1]) / 1024 ** 2
    except Exception:
        pass
    return 8.0


def _gpus() -> int:
    """GPUs CUDA visíveis. faster-whisper roda em CTranslate2, não em torch."""
    try:
        import ctranslate2
        return ctranslate2.get_cuda_device_count()
    except Exception:
        return 0


# Perfis nomeados. `teste` existe para validar o pipeline rápido, sem esperar
# 87 min de large-v3 — a legenda sai com timing um pouco mais frouxo, e como o
# TEXTO vem sempre do roteiro, nada mais muda.
PERFIS = {
    "teste": Perfil("teste", "small", "cpu", "int8", "veryfast", 2,
                    "validação rápida do pipeline; não usar em vídeo publicado"),
    "m2-8gb": Perfil("m2-8gb", "large-v3", "cpu", "int8", "medium", 2,
                     "MacBook Pro M2 8 GB — whisper a ~3,4x realtime (medido)"),
    "workstation": Perfil("workstation", "large-v3", "cuda", "float16", "slow", 6,
                          "GPU CUDA; whisper deve cair de ~87 min para poucos minutos"),
}


def perfil() -> Perfil:
    forcado = os.environ.get("PERFIL", "").strip()
    if forcado:
        if forcado not in PERFIS:
            raise SystemExit(f"PERFIL desconhecido: {forcado}. Opções: {', '.join(PERFIS)}")
        return PERFIS[forcado]

    if _gpus() > 0:
        return PERFIS["workstation"]

    ram, cpus = _ram_gb(), os.cpu_count() or 4
    if ram >= 32 and cpus >= 12:
        # muita CPU e nenhuma GPU: vale paralelizar mais, mas whisper segue em CPU
        base = PERFIS["workstation"]
        return Perfil("cpu-forte", base.whisper_modelo, "cpu", "int8", "slow",
                      min(8, cpus // 2), "sem GPU, mas com CPU/RAM de sobra")
    return PERFIS["m2-8gb"]


if __name__ == "__main__":
    p = perfil()
    print(p)
    print(f"  RAM {_ram_gb():.0f} GB | {os.cpu_count()} CPUs | {_gpus()} GPU(s) CUDA")
    if p.nota:
        print(f"  {p.nota}")
