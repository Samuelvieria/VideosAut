# Rodar em outra máquina

Runbook de instalação. Comandos em ordem; cada bloco tem uma verificação no fim.

---

## 1. Repositório

```bash
git clone https://github.com/Samuelvieria/VideosAut.git
cd VideosAut
git checkout preparacao-workstation
```

O trabalho está na branch `preparacao-workstation`, não na `main`.

---

## 2. Dependências do sistema

**macOS**
```bash
brew install python@3.12 ffmpeg espeak-ng
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv ffmpeg espeak-ng
```

O `espeak-ng` é obrigatório: o Kokoro usa ele para fonemas em português. Sem ele
o TTS falha na importação, não no uso — o erro aparece longe da causa.

**Windows** — testado em 27/08/2026 numa workstation com RTX 3060 8GB, sem
`winget`/`choco`/`scoop` disponíveis. Sem gerenciador de pacotes, é tudo manual:

```powershell
# Python 3.12 — NÃO usar 3.13: numpy/kokoro não têm wheel pronta pra 3.13 ainda
# e o pip cai pra compilar do fonte com um gcc velho que não builda. Baixar o
# instalador em python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe e rodar:
python-3.12.10-amd64.exe /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1

# ffmpeg — sem choco, baixar build pronto (zip, não precisa de 7-Zip):
# https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip
# Extrair e colocar o `bin\` no PATH do usuário.

# espeak-ng — NÃO precisa instalar no sistema. O `misaki` (dependência do
# Kokoro) já traz o pacote `espeakng-loader`, que empacota o espeak-ng via pip
# e funciona sem instalação global. pipeline/s2_tts.py já está com o wiring
# (EspeakWrapper.set_library/set_data_path) — só rodar `pip install kokoro`
# de novo abaixo já resolve. (O instalador .msi oficial falha sem admin —
# erro 1603 — e nem vale a pena perseguir.)
```

O `espeak-ng` é obrigatório em qualquer SO: o Kokoro usa ele para fonemas em
português. Sem ele o TTS falha na importação, não no uso — o erro aparece
longe da causa.

**Verifica:**
```bash
ffmpeg -version | head -1
ffmpeg -hide_banner -filters | grep -c "drawtext\|zoompan\|sidechaincompress"
```
O segundo tem que devolver `3`. Se devolver menos, o build do ffmpeg é incompleto
e o render vai quebrar no meio.

---

## 3. Ambiente Python

**macOS/Linux**
```bash
python3.12 -m venv .venv
source .venv/bin/activate          # bash/zsh
# source .venv/bin/activate.csh    # tcsh/csh
pip install --upgrade pip
pip install kokoro soundfile numpy faster-whisper pyyaml
```

**Windows**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install kokoro soundfile numpy faster-whisper pyyaml requests
```

**Verifica:**
```bash
python -m pipeline.perfil
```

Esta é a verificação mais importante da migração:

| resposta | significa |
|---|---|
| `workstation` com `cuda/float16` | GPU sendo usada. Legendas caem de ~87 min para poucos minutos |
| `cpu-forte` ou `m2-8gb` | **GPU não detectada** — ver Problemas conhecidos, item 1 |

Essa checagem só confirma que o CUDA é **visível**. Rodar de fato em GPU exige
mais uma coisa — ver item 5 de Problemas conhecidos.

---

## 4. Segredos e arquivos que o git não leva

### 4.1 Credencial do Google

Copie o JSON da conta de serviço para a máquina nova e proteja:

```bash
mkdir -p ~/.config
cp /caminho/do/pendrive/gcloud-tts.json ~/.config/gcloud-tts.json
chmod 600 ~/.config/gcloud-tts.json
```

### 4.2 Chaves

```bash
cp .env.example .env

python -m pipeline.config set FAL_KEY
python -m pipeline.config set ANTHROPIC_API_KEY
python -m pipeline.config set GOOGLE_APPLICATION_CREDENTIALS
```

Cada comando abre um prompt oculto: **cole uma vez e tecle Enter**. Nada aparece
na tela — é campo de senha, é assim mesmo. Ele valida o formato antes de gravar e
recusa comando colado por engano.

Alternativa: copiar o `.env` inteiro por AirDrop/pendrive. Nesse caso rode
`chmod 600 .env` depois.

### 4.3 Biblioteca de sons

```bash
mkdir -p sons
cp /caminho/do/pendrive/sons/*.mp3 sons/
```

88 MB, 12 arquivos. **É o único item insubstituível** — veio de download externo.
Tudo o mais o pipeline refaz. Ver [docs/biblioteca-sons.md](docs/biblioteca-sons.md).

**Verifica:**
```bash
python -m pipeline.config
ls sons/*.mp3 | wc -l          # esperado: 12
```

As três chaves têm que aparecer com prefixo e tamanho. O diagnóstico nunca mostra
o valor inteiro.

---

## 5. Produzir o vídeo

```bash
python -m pipeline.s2_tts      fase0/video-02     # ~12 min — narração por cena
python -m pipeline.s3_imagens  fase0/video-02     # ~50 s, ~R$ 0,60 — 20 cenas
python -m pipeline.s5_render   fase0/video-02     # ~8 min — vídeo final
python -m pipeline.s4_legendas fase0/video-02     # 87 min em CPU, minutos em GPU
```

Saída: `fase0/video-02/final.mp4` e `legendas.pt-BR.srt`.

As imagens não vêm no clone (`imagens/` está no `.gitignore`), mas a seed é fixa
por cena: o `s3_imagens` reproduz exatamente as mesmas 20.

**Todos os estágios são idempotentes.** Rodar de novo sem mudar nada leva
segundos. Se refizer tudo na segunda vez, a idempotência quebrou — abra issue.

Para testar rápido sem esperar o modelo grande:
```bash
PERFIL=teste python -m pipeline.s4_legendas fase0/video-02   # ~17 min
```

---

## Problemas conhecidos

**1. `pipeline.perfil` não diz `workstation` mesmo com GPU**

O `faster-whisper` roda em CTranslate2, não em torch, e o wheel padrão do PyPI é
CPU. Instale a variante com CUDA. Sem isso o whisper roda a 3,4× realtime e
**nada avisa** que era para ser melhor.

**0. O shell do Samuel é tcsh, não bash**

`source .venv/bin/activate` FALHA em tcsh com `Bad : modifier in $ '-'` — e
ainda desativa um venv que já estivesse ligado. Em tcsh o certo é
`source .venv/bin/activate.csh`.

Mais simples e à prova de shell: **não ative nada**, use o caminho direto.

```
cd ~/Videos && ./.venv/bin/python -m pipeline.<estagio> ...
```

Funciona em bash, zsh e tcsh, e não depende de qual janela está ativada. É a
forma que todos os comandos deste runbook deveriam usar.

**2. `command not found: python`**

O venv não está ativo naquela janela. Use o caminho direto, que funciona sempre:
```bash
./.venv/bin/python -m pipeline.config
```

**3. `Command not found.` com maiúscula e ponto**

Seu shell é tcsh/csh, não bash. Use `source .venv/bin/activate.csh`, e note que
`VAR=valor` não funciona em csh (seria `setenv VAR valor`).

**4. Render trava e não termina**

Quase sempre é `-t` colocado antes do `-i` num comando ffmpeg com `zoompan`: o
filtro passa a gerar milhões de frames. `-t` é opção de **saída**. Ver
[pipeline/README.md](pipeline/README.md).

**5. Windows: `perfil` diz `workstation`/`cuda` mas o `s4_legendas` quebra com
`Library cublas64_12.dll is not found or cannot be loaded`**

`ctranslate2.get_cuda_device_count()` (usado pelo `perfil.py`) só confirma que
o driver NVIDIA está visível — não que o runtime CUDA (cuBLAS/cuDNN) existe no
sistema. No Windows normalmente não existe, a menos que o CUDA Toolkit tenha
sido instalado à parte. Resolve sem precisar do Toolkit inteiro:

```powershell
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Isso instala os `.dll` dentro do próprio venv
(`.venv\Lib\site-packages\nvidia\{cublas,cudnn}\bin\`), mas o Windows não
procura DLL em `site-packages` sozinho — falta colocar essas duas pastas no
PATH (do usuário, para persistir):

```powershell
$p1 = "$PWD\.venv\Lib\site-packages\nvidia\cublas\bin"
$p2 = "$PWD\.venv\Lib\site-packages\nvidia\cudnn\bin"
[Environment]::SetEnvironmentVariable("Path", "$([Environment]::GetEnvironmentVariable('Path','User'));$p1;$p2", "User")
```

Medido em 27/08/2026, RTX 3060 8GB: 30 min de áudio transcrito com `large-v3`
em **6 min** (carga do modelo incluída), contra ~87 min em CPU na M2. É o
ganho que justifica a máquina inteira.

---

## O que NÃO mudar na máquina nova

**Resolução de geração continua 640×360.** É decisão estética, não limitação de
hardware — pixel art é upscalado com `flags=neighbor` em escala inteira ×3. Gerar
em 1080p nativo produz pseudo-pixel-art com grade inconsistente.

**`s1_roteiro.py` e `s6_upload.py` continuam não existindo** até 2–3 vídeos
publicados. Mais hardware não valida produto.

Contexto completo em [CLAUDE.md](CLAUDE.md) e
[docs/migracao-workstation.md](docs/migracao-workstation.md).
