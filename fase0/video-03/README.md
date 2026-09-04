# Vídeo 03 — A Luz da Baía Quieta (30 min)

Segundo episódio do formato definitivo. Diferente do video-02: **história
original**, não adaptação de obra existente — de propósito, pra fugir de
histórias muito difundidas (mitologia grega, épicos conhecidos).

## Conceito

Demétrio, um velho contador de histórias grego (persona `filosofo-grego`,
voz `pm_alex`), narra uma noite específica da própria juventude como
guardião de um farol numa ilha pequena — tende o fogo, pensa no filho
(Míron) que foi pro mar há anos, vê dois navios passarem em segurança na
baía. Sem deuses, sem monstros, sem batalha — só um homem, um fogo, e uma
baía quieta.

## Estado

- [x] `roteiro.md` — 2.147 palavras, história original, 20 cenas narradas + 1 cauda
- [x] `plano.json` — 21 cenas, 1800s alvo, prompt de imagem por cena
- [x] `estilo.yaml` — identidade visual (mesma base do canal, ambientação grega)
- [ ] **Roteiro em revisão humana — não rodar TTS/imagens até aprovar**
- [ ] Narração (`s2_tts`) — voz `pm_alex`/0.95 nunca foi calibrada por ouvido
- [ ] Imagens (`s3_imagens`)
- [ ] Mix + render (`s5_render`)
- [ ] Legendas (`s4_legendas`)
- [ ] Thumbnails

## Como gerar (depois da revisão do roteiro)

```
python -m pipeline.s2_tts       fase0/video-03
python -m pipeline.s3_imagens   fase0/video-03
python -m pipeline.s5_render    fase0/video-03
python -m pipeline.s4_legendas  fase0/video-03
```

## Correções de prompt aplicadas em 03/09/2026

O plano veio da outra máquina montado a partir do template de **antes** das
correções do video-02. O `s3_imagens --seco` pegou três regressões antes de
gastar um centavo:

1. `estilo_base` tinha `painterly game background art` — o cue que escreveu
   "Moby-Dolk" na tela do video-02. Removido.
2. `estilo_base` fixava `at night`, contradizendo a cena 6 (memória diurna),
   a 20 e a 21 (amanhecer). Removido — as 21 cenas já trazem a própria luz.
3. `obra` estava em português e com negações (`sem deuses, sem monstros`), que
   em prompt positivo pedem o que negam. Reescrito em inglês, sem o título
   original, que não carrega informação visual e só arrisca virar texto na tela.

As quatro regras que saíram disso estão em
`.claude/skills/qualidade-producao-video/references/prompt-imagem.md`.

## Expandido para 73 min em 04/09/2026

Decisão do Samuel depois da pesquisa de mercado. **Velocidade da narração
mantida** em `speed 0.60`.

| | antes | agora |
|---|---|---|
| duração | 30 min | **73 min** (64 de fala + 9 de cauda) |
| cenas | 21 | **39** |
| palavras | 2.157 | **6.481** |

**As 18 cenas novas não esticam o arco emocional.** Um homem esperando uma
noite não rende 64 minutos, e forçar isso vira enchimento. O que rende é o
material **enumerável** que a história já permitia e não usava: como a bacia de
bronze funciona, por que a placa refletora precisa ser polida, o que a mecha
faz se ninguém aparar, de onde vem o óleo, que navios passavam ali, como se
navegava sem nenhuma luz. É a fórmula do History at Night — moldura emocional,
corpo expositivo.

Três cenas vieram de fio solto do próprio roteiro: a mulher dele era citada uma
vez, num copo lascado, e nunca explicada.

Contrato de voz (`docs/voz.md`): **9 de 9 métricas passam.**

Revisado pelo `gemini-3.1-pro`, que achou quatro problemas, todos corrigidos:

1. Eu escrevi "O que se come numa ilha" sem notar que "Pão e vinho" já cobria
   isso — repetindo *"pão duro molhado no azeite"* literalmente nas duas.
2. "O vento tinha nomes" e "Os nomes que ele deu às estrelas" usavam a mesma
   fórmula de fechamento ("um homem sozinho dá nome às coisas").
3. "Pão e vinho" e "O barco do óleo" estavam no terço final, depois da cena de
   risco — logística voltando é um passo atrás. Movidas para o primeiro ato.
4. O barco do óleo já estava estabelecido na cena 6 antes de ganhar cena
   própria.

Ele validou duas coisas: o arco sobrevive, e o primeiro ato virar manual de
operação de farol **é bom para o formato** — ancora em ação concreta e tátil
antes de qualquer peso emocional. E o fecho funciona porque as duas últimas
cenas são descompressão, não clímax.

### Falta antes de produzir

- [ ] Ler o roteiro inteiro em voz alta (ou ouvir a narração) — 9/9 no contrato
      não garante que soa bem
- [ ] Conferir os 38 prompts com `s3_imagens --seco` antes de gastar
- [ ] Gerar imagens: 38 cenas + 3 thumbnails ≈ **R$ 1,00**

## Revisão de plausibilidade histórica (04/09/2026)

Delegada ao `gemini-3.1-pro`. A ambientação é ficção original, mas a descrição
do canal declara que a pesquisa é levada a sério, então erro grosseiro de época
vira comentário.

**Confirmado OK:**

- **Navegação de cabotagem** — navegar de dia com a costa à vista, ancorar de
  noite em enseada. Correto e padrão.
- **`mare clausum`** — a estação de navegar fechando de outubro a março por
  causa das tempestades. Historicamente certo e bem aplicado.
- **Vida material** — pão de cevada duro molhado em azeite, chiton de lã crua,
  sandálias de couro, vinho sempre misturado com água, poço salobro.

**Corrigido:**

- **Tesoura de ferro para aparar a mecha.** Tesoura de eixo (as duas lâminas
  cruzadas num pino) é invenção romana do séc. I d.C. Os gregos tinham tesoura
  de mola, de tosquia, que seria ferramenta estranha para fogo. Trocado por um
  gancho fino de bronze puxando mecha nova, e a parte queimada quebrada com os
  dedos — a rotina repetitiva de hora em hora, que é o que a cena precisa,
  fica intacta. O prompt de imagem da cena também foi corrigido.

**Contestado, e mantido como está:**

O revisor afirmou que faróis antigos queimavam **lenha**, não óleo, e que
azeite era valioso demais para queimar. Fui verificar e a evidência aponta para
o contrário no nosso caso:

- Sobre o Farol de Alexandria, a leitura corrente é *"a fire, likely burning
  **oil** as wood was scarce"*.
- O cálculo que sustenta isso: um fogo de lenha com chama de 2 m consumiria
  **50 toneladas de madeira por noite** — uma floresta por ano. Óleo é o que
  fecha a conta, não o que a estoura.
- Óleo de oliva de **baixa qualidade** para lamparina é padrão absoluto na
  Antiguidade, e o roteiro já especifica exatamente isso: *"óleo ruim, o que
  não servia pra comida — grosso, escuro, com cheiro forte"*.
- A placa de bronze polido como refletor também é atestada nos relatos do
  Farol.

A nossa torre é pequena, com bacia "larga como uma mesa pequena" e uma jarra
durando seis noites — consumo modesto, não uma fogueira imperial. Fica o óleo.

> Registro do método: o revisor errou no ponto principal e acertou no detalhe
> que eu jamais teria pego sozinho. Aceitar tudo teria custado reescrever quatro
> cenas por nada; recusar tudo teria deixado um anacronismo real no texto.

Fontes: [The Past](https://the-past.com/feature/illuminating-antiquity-the-pharos-lighthouse-in-alexandria/) ·
[World History Encyclopedia](https://www.worldhistory.org/Lighthouse_of_Alexandria/)
