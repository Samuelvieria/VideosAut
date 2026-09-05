# video-03 — título, tags e descrição

Escrito em 04/09/2026. **Nada aplicado** — nosso OAuth é `youtube.readonly`.
É para colar no Studio.

Base: [docs/mercado.md](../../docs/mercado.md) §4 e §5, e o
[metadados-revisados.md do video-02](../video-02/metadados-revisados.md), que
corrigiu a regra de título.

---

## O que o vídeo de fato tem

Medido no `plano.json`, ponderado pela duração das cenas:

| camada | presença |
|---|---|
| mar | 38% |
| vento | 35% |
| fogo | 25% |
| **chuva** | **5%** — só 4 cenas de 39 |

**Isso proíbe "som de chuva" no título**, que é o termo com mais busca adulta em
pt-BR. Prometer chuva traria quem quer chuva, e quem quer chuva abandona quando
ouve mar — abandono é o pior sinal que existe. O termo honesto é **som de mar**,
com fogueira em segundo.

Duração: **72,7 min** · narração até 63,7 min + **540 s de cauda exatos** ·
766 legendas. Números do render que saiu na workstation (`duracoes_render.json`),
não estimativa — os 75,9 min anteriores eram de antes da configuração B de voz.

---

## Título

A regra que sobreviveu à evidência (`mercado.md` §4): **o termo que tem busca vem
antes do corte de ~60 caracteres** da busca no celular. Não há ordem única —
entre os vencedores, um põe curiosidade primeiro, outro põe o gênero, e o maior
da amostra tem 35 caracteres e função nenhuma.

Em pt-BR o termo com demanda adulta é o de **ambiente**, e é o único.

**Recomendado** — 55 chars, aparece inteiro em qualquer tela:

> Som de Mar e Fogueira para Dormir | A Luz da Baía Quieta

Alternativas:

| ênfase | título | chars |
|---|---|---|
| mais curto, só efeito | `Som de Mar e Fogueira para Dormir a Noite Toda` | 45 |
| com a promessa da história | `Som de Mar para Dormir \| A Noite do Faroleiro Grego` | 51 |
| recomendado | `Som de Mar e Fogueira para Dormir \| A Luz da Baía Quieta` | 55 |

O que **não** fazer, e a razão está medida:

- **Não** escrever "som de chuva". O vídeo tem 5% de chuva.
- **Não** liderar por "História para Dormir". Esse termo devolve Masha e o Urso
  e Cinderela — mesmo com a palavra "adultos" junto.
- **Não** pôr "A Luz da Baía Quieta" na frente. É título que nós inventamos: o
  público nunca o buscou, então ele não carrega busca nenhuma.

Um risco menor, registrado para não ser esquecido: **"fogueira" promete lenha
estalando, e o nosso fogo é óleo numa bacia de bronze.** Não é o caso da chuva —
fogo está em 28 das 39 cenas, então a camada existe de verdade —, mas quem busca
"som de fogueira" tem uma textura na cabeça. A miniatura mostra um farol, o que
corrige a expectativa antes do clique. Se a retenção dos primeiros segundos vier
ruim, este é o primeiro suspeito.

---

## Tags

Sem tag em inglês — vídeo em português com tag inglesa atrai quem abandona nos
primeiros segundos.

E sem `história para dormir`, pelo mesmo motivo do título: traz pai procurando
desenho animado.

```
som de mar para dormir
som de ondas para dormir
som de fogueira para dormir
barulho de mar relaxante
som de mar e vento
narração calma para dormir
voz calma para dormir
relaxar e dormir
insônia
sono profundo
ruído marrom
grécia antiga
farol antigo
história do mar
conto original
literatura narrada
pixel art
noite tranquila
dormir profundamente
som ambiente para dormir
```

---

## Descrição

```
Um velho faroleiro grego conta a noite em que uma luz apareceu no mar aberto e
respondeu ao sinal dele. Som de mar, de vento e da fogueira do farol por trás.

Sem música. Sem interrupção. A narração vai devagar, e o mar continua por mais
nove minutos depois que a história acaba, para você não acordar no silêncio.

Feito para ouvir deitado, no escuro, com o volume baixo.

──────────────

Sobre como este vídeo é feito

A história é original, escrita por nós — não é adaptação de nenhum texto
existente. A ambientação na Grécia Antiga foi pesquisada: a navegação de
cabotagem, o mar fechado no inverno, a torre de pedra com bacia de bronze e
placa refletora. Onde a pesquisa e a história discordaram, a história cedeu.

A narração é gerada por síntese de voz, e as imagens são geradas uma a uma em
pixel art. O som de mar, vento e fogo é sintetizado, não é gravação de
biblioteca. A divulgação de conteúdo sintético está ativada neste vídeo.

Este é um vídeo de relaxamento, não uma fonte acadêmica.
```

---

## Thumbnails

Três em `thumbnails/`, com o mesmo tratamento: Georgia serifada em creme, sombra
suave, nunca contorno duro.

| | cena | por quê |
|---|---|---|
| A | 3 — A torre e o fogo | o faroleiro acendendo; a mais narrativa |
| **B** | **30 — Uma segunda luz** | **a imagem central da história: a torre e a luz distante respondendo no horizonte. Texto assenta no céu vazio** |
| C | 39 — Mar calmo ao amanhecer | a mais calma; sem personagem |

Minha leitura é a **B**, mas escolher é seu — a folha de contato está em
`thumbnails/contato.png` para comparar as três lado a lado.

Evitei de propósito a cena 17, que é a única de dia: ela quebraria a leitura
noturna na miniatura.

---

## Checklist ao publicar

- [ ] Visibilidade **privada** até você revisar
- [ ] **Anúncios no meio: DESATIVAR** — o padrão liga sozinho acima de 8 min
- [ ] Pré-roll: manter
- [ ] **Conteúdo alterado ou sintético: ATIVADO**
- [ ] Feito para crianças: **não**
- [ ] Idioma: português (Brasil)
- [ ] Enviar `legendas.pt-BR.srt` — reformatado em 04/09 para a norma de
      legibilidade (2 linhas de 42, 1 a 7 s). A versão anterior tinha bloco de
      213 caracteres e dois de duração zero.
- [ ] Capítulos: decisão em aberto (ver `video-02/metadados-revisados.md`); se
      testar, precisa de três ou mais marcações começando em `00:00`

---

# REVISÃO de 05/09/2026 — depois da pesquisa de descrição

O vídeo já está publicado como `KdVNQjzWzNQ`. O que está no ar é bom no
essencial — abre dizendo o que é, tem o bloco de transparência, não pede nada.
Faltam três coisas, e as três atacam o gargalo medido, que é **inscrito** (3) e
não hora de exibição. Base: [docs/descricoes.md](../../docs/descricoes.md).

## Título — com a duração

O que está no ar não diz quanto dura. O espectador escolhe pelo tempo que
precisa cobrir, e às 23h ele não vai medir a barra. É informação **funcional**,
não SEO.

| | chars | |
|---|---|---|
| no ar | 54 | `Som de Mar e fogueira pra Dormir \| A luz da Baía Quieta` |
| **recomendado** | **56** | `Som de Mar e Fogueira para Dormir · 1 Hora · A Luz da Baía Quieta` |
| alternativa exata | 51 | `Som de Mar e Fogueira para Dormir · 1h12 · A Luz da Baía Quieta` |

"1 Hora" **subpromete** 12 minutos, o que é o lado seguro de errar: quem vem
por uma hora ganha mais. O contrário — prometer 1h30 — seria abandono.

Trocar título de vídeo publicado é permitido, e com os Recursos Avançados
ligados dá para rodar o **teste A/B nativo** entre os dois em vez de escolher no
escuro. As três miniaturas já existem em `thumbnails/`.

## Descrição revisada

```
História original para dormir, com som de mar e fogueira ao fundo.
1 hora e 12 minutos, sem música e sem interrupção.
Para adultos — insônia, ansiedade da madrugada, quem simplesmente não desliga.

Um velho faroleiro grego conta a noite em que uma luz apareceu no mar aberto e
respondeu ao sinal dele. A ilha é pequena. A torre é de pedra, e o fogo queima
óleo numa bacia de bronze que precisa de mecha aparada de hora em hora. Ele
fala devagar, sem pressa, como quem já contou isso para si mesmo antes de
contar para alguém.

Não tem batalha. Não tem deus descendo do céu. Não tem monstro no fundo do
mar. Tem um homem, um fogo e uma baía quieta.

A narração ocupa a primeira hora. Depois dela o mar continua sozinho por mais
nove minutos, para você não acordar no silêncio quando a história terminar.

Feito para ouvir deitado, no escuro, com o volume baixo. Se você dormir no
meio, a história continua sem você — é exatamente para isso que ela existe.

──────────────

▶ Todas as histórias, em sequência: COLAR-LINK-DA-PLAYLIST

📄 Sobre como este vídeo é feito

A história é original, escrita por nós — não é adaptação de nenhum texto
existente. A ambientação na Grécia Antiga foi pesquisada: a navegação de
cabotagem, o mar fechado no inverno, a torre de pedra com bacia de bronze e
placa refletora. Onde a pesquisa e a história discordaram, a história cedeu.

A narração é gerada por síntese de voz, e as imagens são geradas uma a uma em
pixel art. O som de mar, vento e fogo é sintetizado por nós, não é gravação de
biblioteca. A divulgação de conteúdo sintético está ativada neste vídeo.

Este é um vídeo de relaxamento, não uma fonte acadêmica.

#somdemar #paradormir #insonia
```

### As decisões desta descrição

**As três primeiras linhas dizem o quê, quanto dura e para quem.** É o que
aparece no resultado de busca e acima do "mostrar mais" — decide o clique junto
com miniatura e título.

**"Para adultos" está na terceira linha, não escondido no fim.** É mitigação de
Made for Kids, que desligaria anúncio personalizado, comentários e notificação
de inscrito. Custa uma linha.

**As hashtags evitam `#historiaparadormir` de propósito.** É o termo mais óbvio
e é o pior dos dois mundos: em busca devolve Masha e o Urso
([mercado.md](../../docs/mercado.md) §4), e em política aproxima o canal do
classificador infantil. `#somdemar #paradormir #insonia` carregam intenção
adulta. Três, porque três é o que o YouTube exibe.

**Nenhum pedido de like, inscrição ou comentário.** Não é esquecimento — é o
formato. Quem acorda com pedido não volta.

**A última linha do primeiro bloco é a promessa central do produto**, e é a
mesma frase que a cena 1 diz em voz: se você dormir no meio, tudo bem.

## O que só você pode fazer

O nosso OAuth é `youtube.readonly` — leio, não escrevo. Três itens, e o
primeiro é o de maior retorno de todos:

- [ ] **Criar a playlist** com os dois vídeos e colar o link no lugar do
      `COLAR-LINK-DA-PLAYLIST`. Quem assiste dois, três, quatro vídeos acaba se
      inscrevendo — e inscrito é o gargalo, não hora.
- [ ] **Ligar a marca d'água de inscrição** (Personalização → Branding). É o
      **único CTA compatível com este formato**: imagem no canto, não faz som,
      não acorda ninguém. Nunca foi configurada.
- [ ] **Desmarcar capítulos automáticos** nos dois vídeos (Detalhes → Mostrar
      mais). O YouTube inventa a divisão e sai bagunçada.
