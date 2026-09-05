---
projeto: Canal de Sono Automatizado
assunto: onde o projeto está e o que fazer a seguir
data: 2026-09-05
status: documento vivo — comece por aqui
substitui: docs/estado-04-09.md (retrato de 03-04/09, mantido como histórico)
---

# Estado e direção

> A versão anterior virou [estado-04-09.md](estado-04-09.md). Não foi editada:
> era um retrato honesto daquele momento, e três coisas grandes mudaram desde
> então. Reescrever por cima apagaria a trilha.

---

## 1. Os números, 05/09/2026

```
canal SleepPowder        3 inscritos  ·  2 vídeos
video-02  Moby Dick      285 views · 13 likes  (4,6% — alto)   publicado 03/09
video-03  A Luz da Baía   32 views ·  0 likes                  publicado 05/09
Analytics                ainda não propagou — nenhuma curva de retenção
```

**A pergunta central do projeto continua sem resposta.** Sem Analytics não há
retenção, e sem retenção não se sabe se o formato funciona. Volte a rodar
`python -m pipeline.s7_metricas --video 103_aYlJr4o` — em canal novo o dado leva
48 a 72 h e o video-02 está em ~46 h.

### O gargalo, medido e não suposto

Não é hora de exibição. É **inscrito**.

| | precisa | temos |
|---|---|---|
| horas (Tier 2) | 4.000 | sem dado |
| **inscritos** | **1.000** (ou 500 no Tier 1) | **3** |

A conversão observada é ~1% (3 em 317 views). Nesse ritmo, 500 inscritos pedem
~50 mil views. **E o formato suprime o mecanismo padrão de conversão**: todo
conselho de crescimento manda pedir inscrição dentro do vídeo, e quem acorda com
"deixe o like" não volta. Isso é estrutural, não descuido.

Os canais que sobram são silenciosos, e **nenhum deles está ligado**:
marca d'água de inscrição, playlist com autoplay, descrição e comentário fixado.

---

## 2. O prazo que apareceu

**01/02/2027 o YPP dobra para 8.000 horas** para quem entra novo (verificado no
blog oficial; quem já está dentro não muda). Faltam ~5 meses.

Isso torna a **duração** a alavanca mais forte que temos:

| duração | AVD | views para 4.000 h |
|---|---|---|
| 10 min | 4 min | 60.000 |
| 1 h | 12 min | 20.000 |
| **3 h** | **40 min** | **6.000** |

---

## 3. O que mudou desde 04/09

### Voz: Kokoro → Google Chirp3-HD

A `GOOGLE_APPLICATION_CREDENTIALS` já estava no `.env` desde sempre. A conta
responde **30 vozes Chirp3-HD em pt-BR** e as mesmas em `en-US`, com o mesmo
timbre. R$ 21/mês na cadência quinzenal bilíngue, contra R$ 505 do ElevenLabs.

- Aprovadas em pt-BR: 10, com **`Algenib`** na frente
- Aprovadas em inglês: `Algenib`, **`Algieba`**, `Enceladus`, `Sadachbia`
- **As vozes em inglês são melhores que as em português** — julgamento do
  Samuel. O inglês é o locale primário do modelo, e aparece.
- Espaçamento: `[pause]` na frase e no respiro, **`[pause long]` no parágrafo**.
  Marcação nativa, não silêncio costurado: o modelo planeja a entoação em volta.
- **127 ppm**, medido no roteiro real. Dreamoria, a referência que funciona: 128.

> **A consequência é de roteiro, não de código.** A lentidão passa a vir do
> TAMANHO do texto. Um vídeo de 2 h pede **14.100 palavras** — o video-03 tinha
> 6.375. Não é estilo, é aritmética.

### Política: dois eixos, não um

**Domínio público resolve direito autoral e NÃO resolve monetização.** São
independentes, e a política diz isso literalmente. Isso muda a pauta: narrar
Homero ou Ali Babá é o gatilho de conteúdo reutilizado, que **vale para o canal
inteiro**. O video-02 (Moby Dick) fica exposto; a defesa é que a adaptação é
nossa, e ela precisa de **prova guardada com data**.

**Made for Kids é risco existencial aqui**, não detalhe de upload — desliga
anúncio personalizado, comentários, notificação de inscrito e memberships. Duas
exposições: o título do video-02 lidera com "História para Dormir", e a pixel
art é linguagem de jogo.

**O que a política PREMIA e não temos:** série com personagens recorrentes e
enredo distinto por episódio. Temos originalidade e variação; falta
continuidade.

### Mercado: o produto talvez esteja no idioma errado

Medido em 225 vídeos pela Data API:

| segmento | mediana | quem domina |
|---|---|---|
| PT "história para dormir" | 25 min | **infantil** (José Totoy 21,8 M) |
| PT com "adultos" | 65 min | **meditação** (não monetizável para persona de IA) |
| **EN história adulto** | **147 min** | Get Sleepy, **Sleepless Historian (713 mil)** |

**História narrada para adultos praticamente não tem segmento em português.** Em
inglês tem vários canais maduros, um deles quase idêntico ao nosso conceito.

**Decisão:** não abrir segundo canal. Usar **faixa de áudio** no mesmo vídeo —
um vídeo, duas faixas, dois títulos, duas descrições, **um só patamar de YPP**.
A imagem e o ambiente não têm idioma. Ver
[ingles-canal-separado.md](ingles-canal-separado.md).

---

## 4. O que existe no código agora

| | |
|---|---|
| `s2_tts` | **dois motores** — Kokoro e `google-chirp3`, escolhidos por `voz.engine` |
| `s4_legendas` | norma de legibilidade: 2 linhas de 42, 1 a 7 s, `--reformatar` |
| `s5_render` | `MIXAGEM_PADRAO` = os valores do video-02, aprovados de ouvido |
| `s5b_thumbs` | três candidatas |
| `preflight` | conhece os dois motores; avisa de eco no ambiente |
| `vozes` | gerador multi-motor, nivelamento a −18 LUFS obrigatório |
| `canal` | avatar do canal, com folha de contato a 48px |
| `limpar` | coletor de lixo, imagens e thumbnails intocáveis |
| `s7_metricas` | leitura do canal, somente leitura |

Padrões do estúdio: **120 min**, **127 ppm**, **14.097 palavras** de meta.

---

## 5. O video-04

**Assunto:** Lawrence da Arábia, primeiro da pauta de sete
([proximos-videos.md](proximos-videos.md)). As travessias, não as batalhas.

**É o primeiro vídeo com tudo novo ao mesmo tempo**, e vale saber disso: motor
de voz novo, duração nova, e a faixa em inglês. Se algo sair errado, há três
suspeitos.

| | |
|---|---|
| duração | **2 h** (120 min) |
| roteiro | **~14.100 palavras** em pt-BR |
| voz | `google-chirp3` · `Algenib` · `pt-BR` |
| cenas | ~68 |
| custo | R$ 4 de imagem + R$ 12 de voz por faixa |
| inglês | adaptação **presa ao tempo das cenas**, voz `Algieba` em `en-US` |

### O que falta construir

- [ ] **Faixa de áudio em inglês** — o `s2_tts` já aceita `lang`, mas nada monta
      o `.m4a` único com a duração exata do vídeo. É o item novo de código.
- [ ] Roteiro de 14.100 palavras — o maior trabalho, e é humano

### O que fazer no Studio antes (minutos, e nada depende de render)

- [ ] Ativar **Recursos Avançados** — destrava faixa de áudio E teste A/B
- [ ] Subir a foto de perfil (`fase0/_canal/foto-perfil.png`)
- [ ] Colar a seção Sobre (`fase0/_canal/sobre.md`)
- [ ] **Criar a playlist** e ligar a **marca d'água de inscrição**
- [ ] Desmarcar capítulos automáticos nos dois vídeos

---

## 6. Saldos

| | |
|---|---|
| fal.ai | **US$ 13,65** — ~70 vídeos de imagem |
| Google TTS | US$ 30/milhão. Consumo **não legível pela conta de serviço** (escopo de TTS, não de faturamento) — ver no console |
| Anthropic | não usado em produção; `s1_roteiro` continua proibido |

---

## 7. Dívida aberta

- **Analytics do video-02** — a pergunta central, e ela responde sozinha em
  horas
- **Faixa gratuita do Chirp3-HD** — 1 milhão/mês é inferência de agregador, não
  texto do Google
- **`private` → público dispara notificação de inscrito?** A decisão fixada
  manda subir privado; a fonte recomenda não listado
- **Demétrio vira arco?** Não exige código, exige uma frase — e é o único
  mecanismo que temos para o gargalo de inscrito
- **video-02 e a política de reutilizado** — decidir se reposiciona ou se
  abranda o texto da seção Sobre
- **`s1_roteiro` e `s6_upload`** continuam proibidos até 2–3 vídeos publicados.
  Estamos em 2.
