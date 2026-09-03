#!/usr/bin/env python3
"""s7b — lê as métricas do canal. SOMENTE LEITURA.

    python -m pipeline.s7_metricas                    # lista os vídeos do canal
    python -m pipeline.s7_metricas --video VIDEO_ID   # relatório de um vídeo
    python -m pipeline.s7_metricas --video ID --json  # grava em metricas/

Requer `python -m pipeline.s7_auth` uma vez antes.

Os números que importam neste nicho, em ordem — a lista saiu das consultas
externas em docs/consultas/sintese.md:

  1. retenção em 30s, 60s e 90s   -> diz se cortar a moldura funcionou
  2. duração média ABSOLUTA        -> em sono, 11% de 41min pode ser sucesso:
                                      a pessoa dormiu. Percentual engana aqui.
  3. origem do tráfego             -> busca é o único canal controlável no zero
  4. dispositivo                   -> TV indica uso como rotina noturna

LIMITE CONHECIDO: "novos vs recorrentes" NÃO existe na API pública — é só do
Studio. Recorrente é o número que mais importa no nicho e precisa ser lido à
mão. `subscribedStatus` (inscrito/não) é o mais próximo que a API oferece, e
não é a mesma coisa.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import erro, log, projeto
from pipeline.s7_auth import credenciais

INICIO_PADRAO = "2020-01-01"   # o suficiente para pegar tudo


def _servicos():
    from googleapiclient.discovery import build
    c = credenciais(interativo=False)
    return (build("youtube", "v3", credentials=c, cache_discovery=False),
            build("youtubeAnalytics", "v2", credentials=c, cache_discovery=False))


def _consulta(an, **kw) -> list[dict]:
    """Roda um relatório e devolve linhas como dicionários."""
    r = an.reports().query(ids="channel==MINE", startDate=kw.pop("inicio"),
                           endDate=kw.pop("fim"), **kw).execute()
    cols = [c["name"] for c in r.get("columnHeaders", [])]
    return [dict(zip(cols, linha)) for linha in r.get("rows", [])]


def listar(yt) -> list[dict]:
    ch = yt.channels().list(part="contentDetails,snippet", mine=True).execute()
    itens = ch.get("items") or []
    if not itens:
        erro("a conta autorizada não tem canal")
    uploads = itens[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    vids, token = [], None
    while True:
        r = yt.playlistItems().list(part="snippet,contentDetails", playlistId=uploads,
                                    maxResults=50, pageToken=token).execute()
        for it in r.get("items", []):
            vids.append({"id": it["contentDetails"]["videoId"],
                         "titulo": it["snippet"]["title"],
                         "publicado": it["contentDetails"].get("videoPublishedAt", "?")})
        token = r.get("nextPageToken")
        if not token:
            break
    return vids


def relatorio(yt, an, vid: str) -> dict:
    fim = date.today().isoformat()
    f = f"video=={vid}"
    v = yt.videos().list(part="snippet,contentDetails,statistics", id=vid).execute()
    itens = v.get("items") or []
    if not itens:
        erro(f"vídeo {vid} não encontrado nesta conta")
    info = itens[0]

    out = {"id": vid, "titulo": info["snippet"]["title"],
           "publicado": info["snippet"].get("publishedAt"),
           "duracao_iso": info["contentDetails"]["duration"],
           "estatisticas": info.get("statistics", {})}

    base = _consulta(an, inicio=INICIO_PADRAO, fim=fim, filters=f,
                     metrics="views,estimatedMinutesWatched,averageViewDuration,"
                             "averageViewPercentage,subscribersGained")
    out["resumo"] = base[0] if base else {}

    # curva de retenção: audienceWatchRatio por fração do vídeo (0.00 a 1.00)
    try:
        curva = _consulta(an, inicio=INICIO_PADRAO, fim=fim, filters=f,
                          metrics="audienceWatchRatio",
                          dimensions="elapsedVideoTimeRatio")
        out["curva_retencao"] = curva
    except Exception as e:
        out["curva_retencao"] = []
        log(f"curva de retenção indisponível ({str(e)[:80]})")

    for chave, dim in [("trafego", "insightTrafficSourceType"),
                       ("dispositivo", "deviceType"),
                       ("inscrito", "subscribedStatus")]:
        try:
            out[chave] = _consulta(an, inicio=INICIO_PADRAO, fim=fim, filters=f,
                                   metrics="views,estimatedMinutesWatched",
                                   dimensions=dim, sort="-views")
        except Exception as e:
            out[chave] = []
            log(f"{chave} indisponível ({str(e)[:60]})")
    return out


def _seg(iso: str) -> int:
    import re
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def imprimir(r: dict) -> None:
    dur = _seg(r["duracao_iso"])
    s = r.get("resumo", {})
    print(f"\n  {r['titulo']}")
    print(f"  {r['id']}  |  {dur//60}min{dur%60:02d}  |  publicado {str(r.get('publicado'))[:10]}")
    pub = r.get("estatisticas", {})
    va = int(s.get("views", 0) or 0)
    vp = int(pub.get("viewCount", 0) or 0)
    print(f"\n  PÚBLICO (atualiza em minutos)")
    print(f"    views {vp}  |  likes {pub.get('likeCount','?')}  |  "
          f"comentários {pub.get('commentCount','?')}")
    print(f"\n  ANALYTICS (atrasa horas, até ~48h no começo)")
    if vp and not va:
        print(f"    ainda sem dado — as {vp} views públicas ainda não propagaram")
    print(f"  views {s.get('views','?')}  |  duração média "
          f"{int(s.get('averageViewDuration',0))//60}min{int(s.get('averageViewDuration',0))%60:02d}"
          f"  ({s.get('averageViewPercentage',0):.1f}%)"
          f"  |  inscritos ganhos {s.get('subscribersGained','?')}")

    curva = r.get("curva_retencao") or []
    if curva and dur:
        print(f"\n  RETENÇÃO — o número que decide se cortar a moldura funcionou")
        por_ratio = {float(l["elapsedVideoTimeRatio"]): float(l["audienceWatchRatio"]) for l in curva}
        for seg in (30, 60, 90, 300, 600):
            if seg > dur:
                continue
            alvo = seg / dur
            k = min(por_ratio, key=lambda x: abs(x - alvo))
            print(f"    {seg:>4}s  {100*por_ratio[k]:5.1f}%")
    elif not curva:
        print("\n  (sem curva de retenção — normal nas primeiras 48h ou com poucas views)")

    for chave, rot in [("trafego", "ORIGEM DO TRÁFEGO"), ("dispositivo", "DISPOSITIVO")]:
        linhas = r.get(chave) or []
        if not linhas:
            continue
        tot = sum(int(l.get("views", 0)) for l in linhas) or 1
        print(f"\n  {rot}")
        for l in linhas[:6]:
            nome = l.get("insightTrafficSourceType") or l.get("deviceType") or "?"
            print(f"    {nome:<24}{int(l['views']):>6} views  {100*int(l['views'])/tot:5.1f}%")

    print("\n  NOVOS vs RECORRENTES não existe na API — ler no Studio.")
    print("  É o número que mais importa neste nicho: quem volta toda noite.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Lê métricas do canal (somente leitura).")
    ap.add_argument("--video", help="ID do vídeo; sem isso, lista os vídeos")
    ap.add_argument("--json", action="store_true", help="grava em metricas/<id>-<data>.json")
    a = ap.parse_args()

    yt, an = _servicos()
    if not a.video:
        vids = listar(yt)
        if not vids:
            print("  nenhum vídeo no canal ainda")
            return
        print(f"\n  {len(vids)} vídeo(s):\n")
        for v in vids:
            print(f"    {v['id']}  {str(v['publicado'])[:10]}  {v['titulo'][:56]}")
        print(f"\n  detalhe: python -m pipeline.s7_metricas --video <ID>")
        return

    r = relatorio(yt, an, a.video)
    imprimir(r)
    if a.json:
        d = Path("metricas"); d.mkdir(exist_ok=True)
        p = d / f"{a.video}-{date.today().isoformat()}.json"
        p.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  gravado em {p}")


if __name__ == "__main__":
    main()
