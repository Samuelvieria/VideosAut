#!/usr/bin/env python3
"""s7a — consentimento OAuth do YouTube. Roda UMA vez.

    python -m pipeline.s7_auth [--forcar]

Abre o navegador, você autoriza com a conta do canal, e o token fica em
`~/.config/youtube-token.json` (permissão 600). Nada de credencial passa por
argumento de comando nem aparece na tela.

Escopos de LEITURA apenas. Upload e edição ficariam em `s6_upload.py`, que o
CLAUDE.md proíbe até 2-3 vídeos publicados — pedir escopo de escrita agora só
tornaria a verificação do app mais pesada sem uso.

ATENÇÃO, e é o detalhe que quebra em silêncio: enquanto a tela de
consentimento estiver em "Teste", o refresh token expira em ~7 dias. Para uso
manual tudo bem; num cron, quebra toda semana. Confirmar o status de
publicação antes de automatizar.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import erro, log
from pipeline.config import obter

ESCOPOS = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
TOKEN = Path("~/.config/youtube-token.json").expanduser()


def credenciais(interativo: bool = True):
    """Devolve credenciais válidas, renovando ou pedindo consentimento."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    cred = None
    if TOKEN.is_file():
        try:
            cred = Credentials.from_authorized_user_file(str(TOKEN), ESCOPOS)
        except Exception as e:
            log(f"token existente ilegível ({e}); vou pedir de novo")

    if cred and cred.valid:
        return cred

    if cred and cred.expired and cred.refresh_token:
        try:
            cred.refresh(Request())
            _grava(cred)
            log("token renovado")
            return cred
        except Exception as e:
            log(f"renovação falhou ({e}) — provavelmente o app está em 'Teste' "
                f"e o refresh token expirou. Autorizando de novo.")

    if not interativo:
        erro("sem token válido. Rode: python -m pipeline.s7_auth")

    from google_auth_oauthlib.flow import InstalledAppFlow
    cliente = obter("YOUTUBE_OAUTH_CLIENT")
    if not Path(cliente).is_file():
        erro(f"não achei o JSON do cliente OAuth em {cliente}")
    fluxo = InstalledAppFlow.from_client_secrets_file(cliente, ESCOPOS)
    log("abrindo o navegador — autorize com a conta DO CANAL, não a pessoal")
    cred = fluxo.run_local_server(port=0, prompt="consent")
    _grava(cred)
    return cred


def _grava(cred) -> None:
    TOKEN.parent.mkdir(parents=True, exist_ok=True)
    TOKEN.write_text(cred.to_json(), encoding="utf-8")
    TOKEN.chmod(0o600)


def main() -> None:
    ap = argparse.ArgumentParser(description="Autoriza o acesso de leitura ao canal.")
    ap.add_argument("--forcar", action="store_true", help="ignora o token salvo")
    a = ap.parse_args()
    if a.forcar and TOKEN.is_file():
        TOKEN.unlink()

    cred = credenciais()
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", credentials=cred, cache_discovery=False)
    r = yt.channels().list(part="snippet,statistics", mine=True).execute()
    itens = r.get("items") or []
    if not itens:
        erro("autorizou, mas a conta não tem canal. Crie o canal e rode de novo.")
    c = itens[0]
    print(f"\n  canal     : {c['snippet']['title']}")
    print(f"  id        : {c['id']}")
    print(f"  inscritos : {c['statistics'].get('subscriberCount','?')}")
    print(f"  vídeos    : {c['statistics'].get('videoCount','?')}")
    print(f"\n  token em {TOKEN} (600)")


if __name__ == "__main__":
    main()
