---
projeto: Canal de Sono Automatizado
assunto: procedência de imagem para temas históricos
data: 2026-08-26
status: decisão operacional
---

# Imagens de acervo para temas históricos

**Decisão (26/08/2026):** para vídeos de tema histórico, usar imagens de acervo em
domínio público, além das geradas. Este doc define de onde e sob que disciplina.

O ponto não é "internet ou não". É **acervo que declara o status de direito por
arquivo** versus busca genérica. Os primeiros têm campo de licença legível por
máquina, permalink estável e resolução alta — e são justamente onde está o material
baleeiro bom. Também são automatizáveis na Fase 1; garimpo manual não é.

## Acervos aprovados

| Acervo | O que tem de útil | API | Status |
|---|---|---|---|
| **The Met** | pinturas e gravuras marítimas; 132 resultados para "whaling" | sem chave | **verificado** — expõe `isPublicDomain`, `primaryImage`, `artistDisplayName`, `objectDate` |
| **New Bedford Whaling Museum** | o porto de onde Melville partiu; a coleção baleeira mais relevante que existe | ? | não verificado |
| **Nantucket Historical Association** | porto de origem do Pequod | ? | não verificado |
| **Rijksmuseum** | pintura marítima holandesa, alta resolução | chave grátis | não verificado |
| **Yale Center for British Art** | Turner, open access | ? | não verificado |
| **Smithsonian Open Access** | CC0, acervo enorme | sim | não verificado |
| **NYPL Digital Collections** | material baleeiro, flag de DP | sim | não verificado |
| **Library of Congress** | gravuras do séc. XIX | sim | não verificado |
| **Biodiversity Heritage Library** | pranchas de história natural — anatomia de baleia | sim | não verificado |

Autores seguros por morte (DP inclusive no Brasil):

- **Ambroise Louis Garneray** (1783–1857) — caça à baleia. Melville o elogia
  nominalmente no cap. 56 do próprio livro. A fonte mais legítima para este projeto.
- **J.M.W. Turner** (1775–1851) — baleeiros e tempestade.
- **Gustave Doré** (1832–1883) — mar e naufrágio.

## Registro de origem (leve, sem trava)

**Decisão do Samuel, 26/08/2026:** não gatear imagem por status de direito. A regra
de `autor_morte` obrigatório foi removida — ele avaliou o risco e assumiu.

O que fica, porque custa um campo num JSON que já escrevemos de qualquer jeito:
anotar de onde a imagem veio, para conseguir refazer ou responder rápido se
precisar.

```json
"origem": {
  "instituicao": "The Metropolitan Museum of Art",
  "url": "https://www.metmuseum.org/art/collection/search/437422",
  "autor": "Ambroise Louis Garneray",
  "uso": "referencia_img2img"
}
```

`uso` continua útil por motivo estético, não jurídico: `referencia_img2img` mantém a
identidade pixel art do canal, enquanto `direto` põe uma pintura a óleo no meio de
uma sequência de pixel art e quebra a linguagem visual. Ver `fase0/video-02/estilo.yaml`.

## Nota de referência (não é regra)

Prazos de domínio público divergem entre países: EUA conta a partir da publicação
(95 anos para obras de 1930), Brasil conta morte do autor + 70 (Lei 9.610/98, art. 41).
Um acervo americano marcando "public domain" está falando do prazo de lá. Fica
registrado como informação; não bloqueia nada.
