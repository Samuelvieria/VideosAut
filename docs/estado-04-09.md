---
projeto: Canal de Sono Automatizado
assunto: onde o projeto está, quanto custa, e em que ordem fazer o resto
data: 2026-09-03
status: avaliação de rumo
---

# Estado e direção

> **Atualizado em 04/09/2026, duas sessões.** Feitos: 4.1 (personas com
> estética), 4.2 (thumbnails), 4.3 em parte, e o **4.4 inteiro menos o
> `s6_upload`** — criar projeto, encadear estágios em sequência parando no
> primeiro erro, e um `preflight` que confere tudo antes de gastar. Mais o
> roteiro do video-03 levado a 39 cenas e o achado do piso de `speed`. Relatório em
> [noite-04-09.md](noite-04-09.md). E a pesquisa de mercado
> ([mercado.md](mercado.md)) contrariou duas premissas que este documento
> tratava como dadas — duração e cadência.

Revisão dos 31 documentos do projeto, do código e dos dados reais do canal,
para responder: onde estamos, quanto custa cada vídeo agora que a curva de
aprendizado passou, e em que ordem atacar as oito frentes abertas.

---

## 1. Onde estamos — o número que reordena tudo

O pipeline está pronto e funciona. Cinco estágios mecânicos, idempotentes,
dirigíveis pela interface. Dois vídeos escritos, um publicado. Isso é real e
foi caro de conseguir.

E o canal tem isto:

```
História para Dormir com Som de Chuva e Mar | Moby Dick e a Baleia Branca
publicado 2026-09-03  ·  4 views  ·  1 like  ·  0 comentários
retenção: sem dado
```

**O vídeo foi ao ar hoje.** Não existe leitura de retenção, de origem de
tráfego, nem de espectador recorrente — que o [monetizacao.md](monetizacao.md)
identifica como o número que mais importa neste nicho.

Isso não é crítica ao trabalho feito. É a constatação de que **a pergunta
central do projeto segue sem resposta**, e ela está escrita na última linha da
[síntese das consultas externas](consultas/sintese.md):

> Uma pessoa que quer dormir realmente quer ficar 45 minutos ouvindo isso?

Vale registrar que essa não é opinião minha isolada. Das seis análises externas
independentes, **quatro de cinco** disseram para parar de construir e publicar,
e duas nomearam o `estudio/` como otimização prematura. O CLAUDE.md abre com a
mesma frase, escrita antes de qualquer código: *"o maior risco do projeto não é
técnico — é construir automação eficiente demais para um produto não
validado."*

Você me pediu para avaliar a direção. Essa é a avaliação: **as oito frentes
que você listou são boas, e a maioria delas é cedo.** Não todas — e a diferença
entre as que são cedo e as que não são é o que estrutura o resto deste
documento.

---

## 2. Quanto custa um vídeo hoje

Câmbio de 03/09/2026: **US$ 1 ≈ R$ 5,10** `[SECUNDÁRIO]`.

### Custo em dinheiro

Só um estágio gasta: as imagens.

| item | conta | US$ | R$ |
|---|---|---|---|
| 1 imagem 1280×720 | 0,9216 MP × US$ 0,005/MP | 0,0046 | 0,024 |
| 21 cenas + 3 thumbs | 24 imagens | 0,111 | **0,56** |
| com retentativa 2,5× | 60 gerações | 0,277 | **1,41** |

**Custo marginal por vídeo: R$ 0,56 a R$ 1,41.**
A 13 vídeos/mês: **R$ 7 a R$ 18 por mês.**

TTS (Kokoro local), legendas (whisper local), ambiente (procedural) e render
(FFmpeg) custam **zero**. Não é aproximação — não há chamada paga nesses
estágios.

Ou seja: passada a curva de aprendizado, **o custo em dinheiro deixou de ser
uma variável do projeto.** Qualquer decisão daqui em diante que se justifique
por economia está resolvendo um problema de R$ 18/mês.

### Custo em tempo — este sim é o gargalo

| estágio | M2 8 GB | workstation (previsto) |
|---|---|---|
| `s2_tts` | ~12 min | ~3 min |
| `s3_imagens` | ~2 min | ~2 min (API) |
| `s4_legendas` | **~87 min** | ~10 min (GPU) |
| `s5_render` | ~8 min | ~3 min |
| **total de máquina** | **~110 min** | **~18 min** |

Mais a revisão humana, que não encolhe com hardware: ouvir a narração, conferir
as 21 imagens uma a uma (a lição do "Moby-Dolk" foi ter olhado só 4 de 20),
escrever título e descrição.

**A migração para a workstation vale por si.** Ela devolve ~90 min por vídeo, e
a 13 vídeos/mês são ~19 horas mensais. É o melhor retorno disponível hoje, e
não depende de nenhuma validação de produto para se pagar.

### Se um dia comprarmos voz

| | pt-BR | bilíngue |
|---|---|---|
| Kokoro/Chatterbox (local) | R$ 0 | R$ 0 |
| Fish Audio (uso) | ~R$ 15/mês | ~R$ 30/mês |
| ElevenLabs Pro | R$ 505/mês | R$ 505/mês |

Detalhe importante para o item do inglês: **as imagens são reaproveitadas
integralmente entre idiomas.** Só áudio e legenda dobram. O inglês é barato no
que custa dinheiro e caro no que custa julgamento.

---

## 3. Dívida encontrada na revisão dos .md

Antes dos planos, o que a revisão achou de errado. Isto não é cosmético: foi
exatamente esse mecanismo que fez o video-03 nascer com o bug de prompt que
custou o video-02.

**Quatro documentos prescrevem coisa que o código não faz mais:**

| arquivo | diz | é |
|---|---|---|
| `SETUP.md:251` | gerar em 640×360, escala ×3 | 1280×720, escala ×2 |
| `pipeline/README.md:17,42,45` | saída 640×360, ×3 | 1280×720, ×2 |
| `docs/migracao-workstation.md:65,83` | Draw Things + SD 1.5, 640×360 | fal.ai, 1280×720 |
| `docs/imagens-provedores.md:55,69,77` | idem | idem |

**Duas referências órfãs:**

- `estudio/dados/personas.json` aponta para `fase0/_vozes-candidatas/`, que não
  existe.
- `estudio/routers/pipeline_run.py` citava `docs/estudio-plano.md`, que não
  existe (corrigido em 03/09).

**Uma regra que só virou documento depois de custar duas vezes:** o cue
`painterly game background art` escreveu o título na tela do video-02, foi
corrigido lá, mas nunca foi escrito na skill — e voltou no video-03. Já está
registrado agora.

> A regra geral que sai disso: **o custo de uma lição não é o erro, é a
> reincidência.** Documento que mente é pior que documento que falta, porque o
> segundo faz você olhar o código.

---

## 4. As oito frentes, em ordem de quando fazer

O critério de ordenação não é dificuldade nem preço. É **o custo de estar
errado**. Coisa barata, permanente e útil em qualquer cenário vai primeiro.
Aposta cara em premissa não validada vai depois do dado.

### Agora — barato, permanente, útil mesmo se o canal mudar de rumo

#### 4.1 Personas com estética, não só voz — *seu item 5* · **FEITO 04/09**

Já existem 4 personas em `estudio/dados/personas.json`, com voz pt-BR
configurada. O que falta é o que você pediu: **elas não carregam estética.**
Hoje o visual mora em `fase0/video-NN/estilo.yaml`, por vídeo, e é recopiado a
cada projeto — que foi como o bug do video-03 viajou.

Proposta: a persona passa a carregar também `estilo_base`, paleta, negativos e
o ritmo de pausa. Criar vídeo novo vira escolher persona + escrever roteiro, em
vez de copiar YAML e herdar os erros dele.

Ganho: permanente, e conserta a causa raiz de uma regressão real.
Custo: baixo. Não depende de nenhum dado de audiência.

#### 4.2 Thumbnails padronizadas — *seu item 9* · **FEITO 04/09**

**Não existe nenhuma ferramenta de thumbnail no projeto.** As três do video-02
foram feitas na mão, e nada foi codificado — inclusive os 5 comandos que
falharam pela pegadinha do `$G:text=` no zsh.

Você gostou de ter três opções. Então a padronização é: um estágio que gera
sempre **três variantes de recipe fixo** (ex.: rosto/objeto em close, plano
aberto da cena mais bonita, e uma com faixa de texto), a partir de frames que o
próprio vídeo já tem. Escolher continua sendo seu; gerar deixa de ser artesanal.

Ganho: tira a etapa mais manual que sobrou. Custo: baixo.

#### 4.3 Padronizar o que já sabemos de imagem — *seu item 7* · **PARCIAL**

Você está certo de que os resultados ficaram bons e o padrão tem que continuar.
O risco não é a qualidade cair, é o **conhecimento estar espalhado**: parte no
CLAUDE.md, parte na skill, parte em `estilo.yaml`, parte em `plano.json`, e
quatro documentos ainda ensinando a resolução errada.

Três ações concretas, todas de custo zero:

1. Corrigir os quatro documentos com prescrição velha (§3).
2. Mover o que é invariante do canal (traço, paleta, negativos) para a persona
   (§4.1), deixando no vídeo só o que muda de episódio.
3. Adotar as duas técnicas que a síntese externa trouxe e nunca aplicamos:
   **direção de luz fixa** em todas as cenas ancora estilo mais que o assunto, e
   **paleta com 3–4 cores nomeadas** explicitamente no prompt.

E um lead novo, da pesquisa do repo `ecc`: a fal.ai expõe **img2img** e
`estimate_cost`. Usar uma cena aprovada como referência de img2img (denoising
baixo, 0,30–0,55) é a técnica que a síntese aponta como o topo real da
hierarquia de consistência — acima de prompt e de seed. Vale testar no video-03.

### Depois de publicar mais dois vídeos

#### 4.4 O aplicativo mais autônomo — *seu item 8* · **quase todo FEITO**

O estúdio dirige os oito estágios, cria projeto a partir de persona, encadeia
sequências parando no primeiro erro, e roda um `preflight` antes de tudo. Só o
`s6_upload` continua de fora, e por regra sua.

O que faltava, em ordem:

1. ~~**Criar projeto pela interface**~~ — **FEITO 04/09.** Nasce de uma persona,
   com o padrão de duração do mercado (75 min) e as validações de prompt.
2. ~~**Encadear estágios**~~ — **FEITO 04/09.** Duas sequências, `mecanica`
   (não gasta) e `completa`, com `preflight` como primeiro passo e parada no
   primeiro erro. Parar importa: os estágios dependem uns dos outros, e seguir
   depois de uma falha produz vídeo com cena faltando em vez de erro.
3. **`s6_upload`** — e aqui há uma trava **sua**, não minha: o CLAUDE.md proíbe
   `s1_roteiro.py` e `s6_upload.py` até 2–3 vídeos publicados. Temos um. Isso
   destrava publicando o video-03 e o video-04, não reescrevendo a regra.

Sobre postar sozinho no YouTube: tecnicamente é o estágio mais simples de todos
(`videos.insert` + `captions.insert`, OAuth já funcionando em modo leitura).
O que ele exige é **o gate manual continuar existindo** — o CLAUDE.md já
determina que todo upload sobe como `private` e você aprova. Isso não é
formalidade: é o que também contorna a trava automática de projetos de API não
auditados, e é o que separa "automação" de "publicar sem olhar".

Legenda e descrição por API (o "depois" que você mencionou) é a parte fácil, e
cai no `s1_roteiro` — mesma trava.

#### 4.5 Voz — *seu item 4*

Você pediu para ir até o fundo antes de gastar. Fui: está em
[tts-provedores.md](tts-provedores.md). O resumo em três linhas:

- Nosso volume é ~15 mil caracteres/vídeo. O ElevenLabs Creator **não cobre**;
  o degrau seguinte é o Pro, a R$ 505/mês.
- O **Fish Audio** sai a ~R$ 15/mês no mesmo volume, e lidera um teste A/B cego
  com margem grande.
- **Nenhum benchmark de 2026 mede pt-BR.** Todos são em inglês.

Por isso a ação não é comprar, é **prova cega**: mesmo trecho de 90 s do
video-02 em Kokoro, Chatterbox, Fish Audio e ElevenLabs, arquivos nomeados
A/B/C/D, ouvidos no fone à noite, revelação só depois. O método é o mesmo que
achou o `aecho` que cinco medições minhas tinham dado como limpo.

Isso pode ser feito a qualquer momento e é barato. O que deve esperar é a
**assinatura**.

### Depois de ter dado de retenção

#### 4.6 Inglês — *seu item 3*

Você está certo no que motiva: o mercado de língua inglesa paga 3–5× mais, e as
imagens saem de graça porque são reaproveitadas. O plano é viável.

Mas as consultas externas se dividiram 3×2 sobre começar pelo inglês, e o lado
minoritário argumenta melhor:

> Em conteúdo de sono, a qualidade da voz **é** o produto. Se a narração em
> inglês for ruim, o canal não converte e você nunca vai saber se foi a voz, o
> roteiro ou o algoritmo. RPM maior não compensa dados contaminados por um
> produto que você não consegue avaliar.

Concordo, e acrescento o que o [voz.md](voz.md) já registra: **a adaptação não
é tradução.** O texto foi escrito para ser falado em português; traduzido vira
prosa engessada. Cada vídeo em inglês é um roteiro reescrito, não um arquivo
convertido — e uma lista de tiques diferente (`delve`, `tapestry`, `testament
to`, `navigate the complexities`).

Decisão de arquitetura que dá para tomar desde já, porque é reversível e não
custa nada: **faixa de áudio multi-idioma no mesmo vídeo (MLA), não canal
separado.** Os dois modelos que defenderam MLA citaram documentação oficial do
YouTube e o dado de que criadores com múltiplas faixas tiveram >25% do watch
time vindo de idiomas não primários. Os três que defenderam canais separados
argumentaram por teoria de algoritmo. Documentação ganha de teoria.

**Pré-requisito real:** uma voz em inglês que você julgue boa. Hoje as quatro
personas têm `en: TBD`. Ou seja — o inglês depende do item 4.5, não o
contrário.

#### 4.7 Outros formatos — *seu item 6*

Concordo com testar variação, e há uma pendência forte: **6 de 6 consultas
disseram que 33 min é errado** — "vale da morte", curto para rotina noturna e
longo para gatilho de sono. Não houve acordo sobre o certo (45–60 min: 3 votos;
120 min: 2). O video-02 saiu com 41 min; o video-03 está planejado com **30**,
que vai na direção contrária do único ponto em que todos concordaram.

Fila proposta, **uma variável por vez** — que é a recomendação mais importante
do lote de consultas:

| teste | muda | por quê |
|---|---|---|
| A | duração 41 → 60 min | o único consenso 6/6 ainda não testado |
| B | ambiente puro, sem narração | testa se a narração é o produto ou o obstáculo |
| C | 2ª pessoa imersiva vs 3ª pessoa | `voz.md` já separa os dois modos |
| D | voz nova (depois de 4.5) | só depois de A ter dado leitura |

O aviso que veio junto: *"não mudaria simultaneamente duração + voz + áudio +
estrutura + imagens, porque aí vocês perdem justamente o que fizeram bem — usar
evidência para decidir."*

---

## 5. O que eu faria nas próximas duas semanas

1. **Publicar o video-03.** Os prompts já estão corrigidos; falta produzir. É o
   segundo vídeo, e é o que destrava `s1_roteiro`/`s6_upload` pela sua regra.
2. **Corrigir os quatro documentos com prescrição velha.** Meia hora, e fecha a
   causa raiz de uma regressão que já aconteceu duas vezes.
3. **Personas com estética + criar projeto pela interface.** As duas peças que
   fazem o estúdio fechar o ciclo, e que tornam o vídeo-04 mais barato de fazer.
4. **Prova cega de voz.** Barata, e você já quer a resposta.
5. **Migrar para a workstation.** Devolve ~19 h/mês e não depende de validação.
6. **Ler os dados do video-02** quando houver 48–72 h de vida.

O que eu **não** faria ainda: assinar TTS, abrir a faixa em inglês, ou escrever
o `s6_upload`. Não por serem ruins — pelo motivo que os seis modelos externos e
o seu próprio CLAUDE.md dizem com palavras diferentes: são otimizações de uma
função cujo valor ainda não foi medido.

E há um argumento a mais, que é o mais afiado do lote e não é sobre eficiência:

> Quanto melhor você constrói a fábrica antes de provar o produto, maior fica a
> tentação de produzir exatamente aquilo que a política chama de problemático.

---

## 6. Um viés meu, declarado

Escrevi este documento defendendo "medir antes de construir", e sou a parte
deste projeto que só sabe construir. Vale desconfiar disso na medida certa: se
os dados do video-02 vierem bons, quase tudo aqui muda de ordem, e as frentes
que empurrei para depois viram as próximas.

O que eu não mudaria em nenhum cenário é a §3 — a dívida de documentação — e a
migração de hardware. Essas duas se pagam mesmo que o canal inteiro mude de
formato amanhã.
