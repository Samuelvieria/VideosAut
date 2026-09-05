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

Revisada em 04/09 por dois defeitos medidos na versão anterior, ambos contra
regra que já estava escrita nos nossos próprios docs:

1. **180 palavras.** A regra é ≥200 — descrição curta rende menos em busca.
2. **A palavra-chave não estava na primeira frase.** `som de mar` aparecia só
   na segunda. O termo com busca tem que abrir a descrição, como abre o título.

O que **não** mudou, de propósito: a honestidade sobre síntese de voz e imagem,
a promessa dos nove minutos de mar depois da história, e a instrução de ouvir
deitado com volume baixo. Ganhou também o aviso de não ouvir dirigindo, que já
está falado nos primeiros 30 s do áudio e não custa nada repetir aqui.

```
Som de mar e fogueira para dormir, com a história de um velho faroleiro grego —
a noite em que uma luz apareceu no mar aberto e respondeu ao sinal dele.

Sem música. Sem interrupção. A narração vai devagar, e o mar continua por mais
nove minutos depois que a história acaba, para você não acordar no silêncio.

Feito para ouvir deitado, no escuro, com o volume baixo. Não escute enquanto
dirige ou opera máquinas.

──────────────

O que você vai ouvir

Som de mar, de vento e do fogo do farol — uma bacia de óleo queimando no alto
de uma torre de pedra. Não tem chuva, não tem música, não tem sino nem
sobressalto: nada no áudio sobe de volume de repente.

A voz é a de Demétrio, um homem velho contando uma noite da própria juventude.
Ele fala devagar, e a história não tem clímax nem final surpreendente. Ninguém
precisa chegar ao fim — se você dormir no meio, ela era para isso.

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

## Playlists — o buraco maior desta lista

Auditando esta página em 04/09 contra a nossa própria estratégia de canal, esse
foi o único item que **não existia em lugar nenhum**: nem aqui, nem no
`monetizacao.md`, nem no checklist. Só aparecia nas consultas a modelos
externos, que os três levantaram sem serem perguntados.

Por que importa mais neste nicho que em qualquer outro: **o espectador quer
fluxo contínuo sem decidir nada.** Ele está deitado, no escuro, com um dedo.
Playlist com autoplay não é organização de catálogo — é o produto. Quem dorme
no video-03 e emenda no video-02 dá duas sessões pelo preço de uma, e tempo de
exibição é exatamente a métrica que abre o YPP.

Com **dois** vídeos publicados isso já funciona, e é a alavanca mais barata que
existe agora: não custa render, não custa API, não custa roteiro.

O que criar (nome com o termo que tem busca, não com o nome que inventamos):

| playlist | o que entra | por quê |
|---|---|---|
| **Som de Mar para Dormir** | video-02 e video-03 | os dois têm mar; é a que forma a corrente de sessão |
| **Histórias Longas para Dormir** | os dois | agrupa por formato, pega quem busca por duração |
| **Todos os Vídeos — Ordem de Publicação** | os dois | catálogo; barata de manter |

Duas coisas para não errar:

- **Descrição e título da playlist também são indexados** — escrever o termo de
  busca neles, não deixar em branco.
- Adicionar o **video-02 também**, não só este. Ele já está no ar e hoje não
  está em playlist nenhuma, então não puxa ninguém para lugar algum.

## Teste A/B de miniatura — dá para usar, com uma ordem específica

Nós já geramos **três** miniaturas, que é exatamente o que o teste nativo do
YouTube aceita. Escolher uma no olho joga fora uma medição de graça.

Dois detalhes operacionais que mudam a ordem do checklist:

- **Vídeo privado não entra no teste.** O teste só existe para vídeo público ou
  não listado — então ele é montado DEPOIS da revisão, não junto do upload.
- Exige **recursos avançados** ativados em Studio → Configurações → Canal →
  Qualificação para recursos → Recursos avançados. Se o botão não aparecer, é
  aqui que se olha primeiro.
- O teste **não penaliza** o vídeo que participa.

Fontes: [guia de teste A/B](https://www.thumbmagic.co/blog/ab-test-youtube-thumbnails).

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

Depois de tornar público (nesta ordem, porque privado não aceita as duas
últimas):

- [ ] Adicionar às **3 playlists** da seção acima — e pôr o **video-02** nelas
      também, que hoje não está em nenhuma
- [ ] Montar o **teste A/B** com as três miniaturas já geradas
- [ ] Horário: a hipótese do doc de estratégia é publicar 3–5 h antes do pico de
      sono (~17h–19h BRT). É hipótese, não dado — vale medir no Studio depois
