"""Cria um projeto de vídeo em fase0/ a partir de uma persona.

Existe porque o visual e a voz vinham sendo copiados de `fase0/video-NN/` para
o próximo projeto à mão, e o erro viajava junto: o video-03 nasceu com o cue
`painterly game background art` que já tinha sido corrigido no video-02, e com
um `obra` em português cheio de negações. Nascer de uma persona validada fecha
as duas portas.

O que é gerado:

    fase0/<slug>/plano.json    <- o que os estágios leem
    fase0/<slug>/estilo.yaml   <- referência humana; o pipeline NÃO lê
    fase0/<slug>/roteiro.md    <- esqueleto, para escrever
    fase0/<slug>/README.md     <- estado do projeto

O pipeline lê exatamente seis chaves de topo do plano — `cenas`,
`duracao_alvo_s`, `estilo_base`, `mixagem`, `obra`, `voz` — e por cena `n`,
`dur_s`, `papel`, `titulo`, `personagem`, `prompt`, `ambiente`, mais os
opcionais `seed_de` e `contexto_narrativo`. Conferido por leitura do código dos
estágios em 04/09/2026, não por suposição.
"""
from __future__ import annotations
import json
import re
from datetime import date
from pathlib import Path

from estudio.db.personas import EsteticaInvalida, obter as obter_persona

RAIZ = Path(__file__).resolve().parent.parent.parent
FASE0 = RAIZ / "fase0"

# MEDIDO em docs/mercado.md §2: não há um só caso de sucesso na amostra perto
# de 30-41 min. A faixa que funciona em narrativa é 65-170 min, e a mediana do
# History at Night (73 mil inscritos com SEIS vídeos) é 76. O padrão do projeto
# passa a ser 75; menor que isso pede justificativa, não o contrário.
DURACAO_PADRAO_MIN = 75
SEG_POR_CENA = 125          # video-02: 2.473 s / 20 cenas = 123,7

# Palavras por minuto de narração, MEDIDO no video-02 sobre os 32,2 min de fala
# real — não sobre os 41 min totais, que incluem a cauda silenciosa. As
# referências rodam a 128 e 180. Ver docs/mercado.md §9.
PPM_MEDIDO = 102

# Valores do video-02, que foi aprovado de ouvido e publicado. Ver
# .claude/skills/qualidade-producao-video/references/mixagem-audio.md
MIXAGEM_PADRAO = {
    "_nota": "Herdado do video-02, aprovado de ouvido. ambiente_reverb=0 porque "
             "o aecho foi identificado como a causa do granulado na cauda.",
    "ambiente_ganho": 0.3,
    "ambiente_reverb": 0.0,
    "ambiente_lowpass_hz": 3500,
    "duck_threshold": 0.05,
    "duck_ratio": 8,
    "duck_attack_ms": 20,
    "duck_release_ms": 900,
    "voz_ganho": 1.0,
    "voz_reverb": 0.0,
    "voz_deesser": True,
}


class ProjetoInvalido(ValueError):
    """Entrada recusada antes de escrever qualquer arquivo."""


def _slug_valido(slug: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", slug):
        raise ProjetoInvalido(
            "slug: só minúsculas, números e hífen, de 2 a 41 caracteres")
    if (FASE0 / slug).exists():
        raise ProjetoInvalido(f"fase0/{slug} já existe")
    return slug


def _validar_obra(obra: str) -> str:
    """O `obra` entra no prompt POSITIVO de toda cena (ver s3_imagens).

    Duas recusas, ambas de erro real do video-03:

    1. Negação. "sem mitologia, sem deuses, sem monstros" em campo positivo
       pede exatamente mitologia, deuses e monstros.
    2. Acento. É proxy preciso para "isto está em português". Título em
       português vira tipografia ilegível quando o modelo decide desenhá-lo —
       e um título que nós inventamos não carrega informação visual nenhuma,
       porque o modelo nunca o viu. O `obra` deve dizer era e tema em inglês:
       `original story set on the ancient Greek coast — a lighthouse keeper's
       tale`, não `A Luz da Baía Quieta`.
    """
    obra = obra.strip()
    if not obra:
        raise ProjetoInvalido("obra: não pode ser vazio — é o contexto "
                              "narrativo que segura o traço do personagem")
    if re.search(r"\b(sem|no|without|never|not|free\s+of)\s+\w", obra, re.I):
        raise ProjetoInvalido(
            "obra contém negação. Modelo de difusão não processa negação: em "
            "prompt positivo, 'sem deuses' pede deuses. O que não se quer vai "
            "no prompt_negativo da persona.")
    # Só LETRAS fora do ASCII. Pontuação tipográfica (travessão, aspas curvas)
    # é legítima em inglês — o `obra` aprovado do video-03 usa travessão.
    acentos = {c for c in obra if c.isalpha() and ord(c) > 127}
    if acentos:
        raise ProjetoInvalido(
            f"obra tem letra acentuada ({''.join(sorted(acentos))}), sinal de "
            f"que está em português. Escreva em inglês, dizendo era e tema — "
            f"nunca o título inventado, que o modelo nunca viu e só arrisca "
            f"virar texto na tela.")
    return obra


def _compor_estilo(est: dict) -> str:
    """Junta traço + paleta + luz numa string só — o que de fato vai ao prompt."""
    partes = [est["estilo_base"].strip().rstrip(",")]
    paleta = [c.strip() for c in (est.get("paleta") or []) if c.strip()]
    if paleta:
        partes.append("palette of " + ", ".join(paleta))
    if (est.get("luz") or "").strip():
        partes.append(est["luz"].strip())
    return ", ".join(partes)


def _cenas_esqueleto(n_cenas: int, dur_s: int, personagem: str) -> list[dict]:
    """Cenas em branco, com os papéis que o roteiro do video-02 usa."""
    por_cena = round(dur_s / n_cenas)
    cenas = []
    for i in range(1, n_cenas + 1):
        papel = ("abertura" if i == 1 else
                 "fecho" if i == n_cenas else
                 "narrado")
        cenas.append({
            "n": i,
            "dur_s": por_cena,
            "papel": papel,
            "titulo": f"(cena {i})",
            "personagem": personagem,
            "prompt": "",     # a cena diz o assunto, o enquadramento e a LUZ dela
            "ambiente": "",
        })
    return cenas


def criar_projeto(slug: str, titulo: str, obra: str, persona_id: str,
                  duracao_min: int = DURACAO_PADRAO_MIN,
                  n_cenas: int | None = None) -> Path:
    """Gera fase0/<slug>/ a partir de uma persona. Valida ANTES de escrever."""
    slug = _slug_valido(slug)
    obra = _validar_obra(obra)
    titulo = titulo.strip()
    if not titulo:
        raise ProjetoInvalido("título: não pode ser vazio")

    persona = obter_persona(persona_id)
    if persona is None:
        raise ProjetoInvalido(f"persona '{persona_id}' não existe")
    est = persona.get("estetica") or {}
    if est.get("estilo_base"):
        from estudio.db.personas import _validar_estetica
        try:
            _validar_estetica({**est, "estilo_base": _compor_estilo(est)})
        except EsteticaInvalida as e:
            raise ProjetoInvalido(
                f"a composição de estilo_base + paleta + luz da persona "
                f"'{persona_id}' é recusada:\n{e}")
    if not est.get("estilo_base"):
        raise ProjetoInvalido(
            f"a persona '{persona_id}' não tem estética definida. Defina em "
            f"/personas/{persona_id}/editar antes — é ela que impede o projeto "
            f"de nascer com um cue de prompt já corrigido em outro vídeo.")

    if duracao_min < 1:
        raise ProjetoInvalido("duração: pelo menos 1 minuto")
    dur_s = duracao_min * 60
    n_cenas = n_cenas or max(3, round(dur_s / SEG_POR_CENA))

    voz = dict(persona["vozes"]["pt"])
    voz.setdefault("engine", "kokoro")
    voz["nota"] = (f"Persona '{persona_id}' (estudio/dados/personas.json). "
                   + (voz.get("nota") or ""))

    plano = {
        "titulo": titulo,
        "obra": obra,
        "duracao_alvo_s": dur_s,
        "narrado_s": None,
        "cauda_ambiente_s": 540,
        "moldura": {
            "_nota": "Moldura de APRESENTADOR, não de personagem. Ver "
                     "docs/mercado.md §9: os dois canais de referência abrem "
                     "com saudação e fecham com boa-noite, e isso é ritual, "
                     "que é o que constrói espectador recorrente. O que as "
                     "consultas mandaram cortar foi a moldura de personagem "
                     "— um narrador fictício se apresentando.",
            "abertura": "", "fecho": "",
        },
        "voz": voz,
        "ambiente": {"_nota": "Preencher por cena no campo `ambiente`."},
        "mixagem": dict(MIXAGEM_PADRAO),
        "direitos": {
            "_nota": "Imagens geradas; áudio procedural. Divulgação de "
                     "conteúdo sintético ATIVADA no Studio.",
        },
        # paleta e luz entram AQUI, não ficam só no estilo.yaml. O `estilo_base`
        # é a única coisa da estética que chega ao prompt (ver s3_imagens), e a
        # síntese das consultas externas aponta as duas como âncora de estilo
        # mais forte que o assunto. Guardá-las num arquivo que o pipeline não lê
        # seria enfeite.
        "estilo_base": _compor_estilo(est),
        "resolucao": list(est.get("resolucao") or [1280, 720]),
        "_estetica_origem": {
            "persona": persona_id,
            "copiado_em": date.today().isoformat(),
            "_nota": "Cópia da estética da persona no momento da criação. Se a "
                     "persona mudar depois, este projeto NÃO acompanha — é "
                     "snapshot de propósito, para um vídeo já produzido não "
                     "mudar de visual sozinho.",
        },
        "nota_duracoes": "dur_s é alvo; a duração real vem do áudio (s2_tts).",
        "cenas": _cenas_esqueleto(n_cenas, dur_s, ""),
    }

    proj = FASE0 / slug
    proj.mkdir(parents=True)
    (proj / "plano.json").write_text(
        json.dumps(plano, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    estilo = {
        "id": slug, "versao": 1, "gerador": "fal.ai / Z-Image-Turbo",
        "resolucao": list(est.get("resolucao") or [1280, 720]),
        "prompt_prefixo": est["estilo_base"],
        "prompt_negativo": est.get("prompt_negativo", ""),
        "paleta": list(est.get("paleta") or []),
        "luz": est.get("luz", ""),
        "seed": {"base": 20260900 + abs(hash(slug)) % 100},
        "_nota": "Referência humana. O pipeline lê o plano.json, não este "
                 "arquivo — só a seed base é lida daqui por s3_imagens.",
    }
    try:
        import yaml
        texto = yaml.safe_dump(estilo, allow_unicode=True, sort_keys=False)
    except Exception:
        texto = json.dumps(estilo, indent=2, ensure_ascii=False)
    (proj / "estilo.yaml").write_text(texto, encoding="utf-8")

    # 102 ppm é a medição corrigida do video-02 sobre a narração real
    # (docs/mercado.md §9). Usar 80 faria todo roteiro novo nascer
    # curto demais para a duração alvo.
    palavras_alvo = f"{duracao_min * PPM_MEDIDO:,}".replace(",", ".")
    (proj / "roteiro.md").write_text(
        f"""# {titulo}

> Esqueleto gerado em {date.today():%d/%m/%Y} a partir da persona
> `{persona_id}`. O contrato de escrita está em `docs/voz.md` e vale para
> todo roteiro: mediana de 9 palavras por frase, 57% com 10 ou menos, 15%
> começando com "E", zero termos banidos.

> **Meta de volume:** {duracao_min} min. Medido em `docs/mercado.md` §9, os
> canais que funcionam escrevem 13.612 e 21.744 palavras. Nos nossos {PPM_MEDIDO}
> palavras/min medidos isso dá cerca de **{palavras_alvo} palavras** aqui — e o
> video-02 tinha 3.279. Não é estilo, é aritmética: texto de menos não
> preenche a duração.

## Abertura

<!-- Saudação de apresentador, curta. Ver o _nota do bloco `moldura`. -->

## Cenas

<!-- Uma seção por cena, casando com `cenas[]` do plano.json. -->
""", encoding="utf-8")

    (proj / "README.md").write_text(
        f"""# {titulo}

Criado em {date.today():%d/%m/%Y} pelo estúdio, a partir da persona
`{persona_id}`.

| | |
|---|---|
| duração alvo | {duracao_min} min ({dur_s} s) |
| cenas | {n_cenas} |
| voz | {voz.get('voice')} (speed {voz.get('speed')}) |
| resolução | {est.get('resolucao', [1280, 720])[0]}×{est.get('resolucao', [1280, 720])[1]} |

## Estado

- [ ] Roteiro escrito (ver a meta de volume em `roteiro.md`)
- [ ] `prompt` e `ambiente` preenchidos em cada cena do `plano.json`
- [ ] `s3_imagens --seco` conferido antes de gastar
- [ ] Narração, imagens, legendas, render
- [ ] Título com curiosidade na frente e função no sufixo (`docs/mercado.md` §4)
- [ ] Tags do gênero
- [ ] Divulgação de conteúdo sintético ativada
- [ ] **Anúncios no meio DESATIVADOS** (`docs/monetizacao.md`)
""", encoding="utf-8")

    return proj
