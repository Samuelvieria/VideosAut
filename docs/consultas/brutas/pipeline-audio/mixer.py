#!/usr/bin/env python3
"""
Mixador de camadas ambientes.
Gera filter_complex do ffmpeg a partir de uma config declarativa.
Loudnorm em dois passes (medicao real -> normalizacao linear).
"""
import json, subprocess, sys, shlex

SR = 48000

def run(cmd, capture=True):
    return subprocess.run(cmd, capture_output=capture, text=True)

def build_filtergraph(layers, dur):
    parts, labels = [], []
    for i, L in enumerate(layers):
        ch = []
        # loop ja tratado no input (-stream_loop), aqui so o processamento
        if L.get("hp"):    ch.append(f"highpass=f={L['hp']}:poles=2")
        if L.get("lp"):    ch.append(f"lowpass=f={L['lp']}:poles=2")
        ch.append(f"volume={L.get('gain_db',0)}dB")
        if L.get("pan") is not None:            # -1 esq .. +1 dir
            p = float(L["pan"])
            gl, gr = (1-p)/2 + 0.5*(1-abs(p)), (1+p)/2 + 0.5*(1-abs(p))
            ch.append(f"pan=stereo|c0={gl:.4f}*c0|c1={gr:.4f}*c1")
        fi, fo = L.get("fade_in", 0), L.get("fade_out", 0)
        if fi: ch.append(f"afade=t=in:st=0:d={fi}:curve=tri")
        if fo: ch.append(f"afade=t=out:st={dur-fo}:d={fo}:curve=tri")
        if L.get("delay"):                       # entrada atrasada, em segundos
            ms = int(L["delay"]*1000)
            ch.append(f"adelay={ms}|{ms}")
        ch.append(f"atrim=0:{dur}")
        parts.append(f"[{i}:a]" + ",".join(ch) + f"[a{i}]")
        labels.append(f"[a{i}]")
    # normalize=0 e ESSENCIAL: com o default (1) o amix divide por N e afunda tudo
    parts.append("".join(labels) + f"amix=inputs={len(layers)}:normalize=0:dropout_transition=0[mix]")
    return ";".join(parts)

def inputs_args(layers):
    a = []
    for L in layers:
        if L.get("loop"): a += ["-stream_loop", "-1"]
        a += ["-i", L["file"]]
    return a

def measure(path):
    """ffmpeg ebur128 -> LUFS integrado, LRA, true peak"""
    r = run(["ffmpeg","-hide_banner","-nostats","-i",path,
             "-af","ebur128=peak=true","-f","null","-"], capture=True)
    out, res = r.stderr, {}
    for line in out.splitlines():
        s = line.strip()
        for k, tag in [("I:","lufs"),("LRA:","lra"),("Peak:","tp")]:
            if s.startswith(k):
                try: res[tag] = float(s.split()[1])
                except (ValueError, IndexError): pass
    return res

def mix(cfg):
    layers, dur = cfg["layers"], cfg["duration"]
    fg = build_filtergraph(layers, dur)
    tmp = "/tmp/_mix_raw.wav"

    # ---- render cru ----
    cmd = ["ffmpeg","-y","-hide_banner","-nostats"] + inputs_args(layers) + \
          ["-filter_complex", fg, "-map","[mix]",
           "-ar",str(SR),"-ac","2","-c:a","pcm_f32le", tmp]
    r = run(cmd)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)

    # ---- pass 1: medicao ----
    tgt_i  = cfg.get("target_lufs", -23)
    tgt_tp = cfg.get("target_tp", -1.5)
    tgt_lra= cfg.get("target_lra", 11)
    ln = f"loudnorm=I={tgt_i}:TP={tgt_tp}:LRA={tgt_lra}:print_format=json"
    r = run(["ffmpeg","-hide_banner","-nostats","-i",tmp,"-af",ln,"-f","null","-"])
    blob = r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}")+1]
    m = json.loads(blob)

    # ---- pass 2: normalizacao linear ----
    ln2 = (f"loudnorm=I={tgt_i}:TP={tgt_tp}:LRA={tgt_lra}:"
           f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
           f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
           f"offset={m['target_offset']}:linear=true:print_format=summary")
    wav = cfg["out_wav"]
    run(["ffmpeg","-y","-hide_banner","-nostats","-i",tmp,"-af",ln2,
         "-ar",str(SR),"-c:a","pcm_s24le", wav])
    if cfg.get("out_mp3"):
        run(["ffmpeg","-y","-hide_banner","-nostats","-i",wav,
             "-c:a","libmp3lame","-b:a","320k", cfg["out_mp3"]])
    return m, measure(wav)

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    pre, post = mix(cfg)
    print("ANTES :", pre["input_i"], "LUFS | TP", pre["input_tp"], "dBTP | LRA", pre["input_lra"])
    print("DEPOIS:", post)
