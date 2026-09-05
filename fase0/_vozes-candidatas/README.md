# Vozes candidatas — protocolo da prova cega

Diretório citado por `estudio/dados/personas.json`. Existia como referência
órfã até 03/09/2026; agora é o lugar onde a comparação de motores de voz
acontece.

Os `.wav` aqui **não são versionados** (`.gitignore`). O que fica no git é este
protocolo e o resultado.

## Por que prova cega e não benchmark

Nenhum ranking público de 2026 mede pt-BR — todos são em inglês. E neste
projeto o ouvido do Samuel já achou duas vezes um defeito que a medição deu
como limpo (o `aecho` da cauda, e a irregularidade do pan). Ver
[docs/verificacao.md](../../docs/verificacao.md).

Levantamento de preço e licença: [docs/tts-provedores.md](../../docs/tts-provedores.md).

## Protocolo

1. **Trecho fixo:** 90 s do roteiro do video-02. Ele já foi aprovado de ouvido,
   então serve de linha de base honesta. Usar sempre o mesmo trecho.

2. **Candidatos:**

   | letra | motor | licença | custo |
   |---|---|---|---|
   | — | Kokoro `pm_santa` (atual) | Apache-2.0 | zero |
   | — | Chatterbox `language_id="pt"` | MIT | zero |
   | — | Fish Audio | comercial no plano pago | ~R$ 15/mês |
   | — | ElevenLabs | comercial | ~R$ 505/mês |

   Os dois pagos têm camada gratuita suficiente para 90 s.

3. **Nomear `A.wav`, `B.wav`, `C.wav`, `D.wav`** — sorteado, e a correspondência
   guardada em `chave.txt`, que **não se abre antes de ouvir**.

4. **Ouvir no fone e no celular, à noite, no volume de dormir.** Não no alto-falante
   do laptop de dia: o formato é usado deitado, no escuro, baixo.

5. Só então abrir `chave.txt`.

## O que julgar, nesta ordem

1. **Respiração e pausa** — é o que separa "leitura" de "contação". É o eixo em
   que o `speed` baixo do Kokoro falha (estica vogal e consoante por igual e
   soa sedado).
2. **Nasais e sibilância** — `ão`, `ãe`, `õe`, e a palatalização de /t/ e /d/
   antes de /i/. É onde TTS multilíngue quebra em português.
3. **Estabilidade ao longo do trecho** — motor que degrada aos 60 s é inútil
   num vídeo de 40 min.
4. **Timbre** — por último. É o que mais chama atenção e o que menos importa
   para dormir.

## Primeira leva — ritmo, não motor (04/09/2026)

Os motores pagos precisam de cadastro, então a primeira comparação testa o que
dá para testar hoje: **o ritmo**, que `docs/mercado.md` §9 apontou como a
diferença mais concreta entre nós e os canais que funcionam.

Mesmo trecho de 158 palavras do roteiro do video-02, voz `pm_santa`:

| arquivo | speed | pausa | ppm |
|---|---|---|---|
| `kokoro-speed060-atual.wav` | 0,60 | 1,0 | **123** |
| `kokoro-speed075.wav` | 0,75 | 1,0 | 152 |
| `kokoro-speed090.wav` | 0,90 | 1,0 | 195 |
| `kokoro-speed100-pausa.wav` | 1,00 | 1,6 | 205 |

Referência medida: Dreamoria **128 ppm** (5,50 M views), History at Night
**180 ppm** (1,18 M). Fala de conversa fica perto de 150.

**O que ouvir:** a 0,60 o Kokoro estica vogal e consoante por igual, que é o que
o CLAUDE.md descreve como "soa sedado". A 1,00 com pausa crescente a articulação
é natural e a lentidão vem do silêncio entre frases — que é o mecanismo que a
pesquisa de ritmo recomendou e que nunca foi comparado de ouvido contra o
antigo. Essa é a pergunta desta leva: **lentidão por esticar ou lentidão por
pausar?**

Não é prova cega — os arquivos estão nomeados. Para o ritmo isso não atrapalha,
porque o que se julga é qual soa melhor, não qual é qual.

## Resultado

_(preencher depois da escuta — data, ordem de preferência, e a decisão)_

---

## Segunda leva — a prova cega de verdade (04/09/2026)

Rodada depois de o Samuel cobrar: *"cadê a prova cega?"*. Ele tinha razão — eu
havia escrito este protocolo e citado ele três vezes como argumento sem ter
executado nada.

Está em `cega/`: **`A.wav`, `B.wav`, `C.wav`** e um `chave.txt` que **não deve
ser aberto antes de ouvir**.

### O que está sendo comparado

Fish Audio e ElevenLabs seguem precisando de cadastro. Mas o **Chatterbox**
(ResembleAI, MIT, local) não precisava de nada, e estava ao alcance desde o
começo. Os três candidatos são ele e as duas configurações do Kokoro.

### O texto não é genérico

É o da **cena 2**, que contém `manhã` e `água` — as duas palavras que o Samuel
apontou como erradas, ambas em fim de frase. A pergunta deixa de ser "qual voz é
mais bonita" e passa a ser **"qual acerta o defeito que eu ouvi"**.

### O nivelamento, que era obrigatório

Medido antes: o Chatterbox saiu a **−15,99 LUFS** e o Kokoro a **−26,18**. Dez
decibéis de diferença. Em teste de escuta o mais alto ganha sistematicamente, e
comparar assim mediria volume, não voz.

Os três foram normalizados a −20 LUFS com `loudnorm` de dois passes e
`linear=true`. **Sem esse passo o teste não valeria nada.**

### Duas coisas medidas que valem saber depois de ouvir

- O Chatterbox roda a **216 palavras/min** no mesmo texto, contra 165 do
  Kokoro. É rápido demais para sono, mas isso é ajustável — não é defeito de
  voz, e não deve pesar no julgamento.
- O áudio cru dele saiu com **pico 1,040**, ou seja **clipando**. Qualquer uso
  em produção precisaria normalizar antes. O Kokoro saiu em 0,463.
- Custo: o modelo baixou **3,0 GB** para o cache do HuggingFace, e leva ~107 s
  só para carregar num M2 de 8 GB. Para apagar:
  `rm -rf ~/.cache/huggingface/hub/models--ResembleAI--chatterbox`

### Julgue nesta ordem

1. **`manhã` e `água`** — a velocidade e a entonação delas melhoram em algum?
2. **Respiração e pausa** — qual soa como quem conta, não como quem lê?
3. **Nasais** — `ã`, `õ`, e a palatalização de /t/ e /d/ antes de /i/.
4. **Timbre** — por último, e de propósito.

---

## Terceira leva — Google Chirp3-HD (05/09/2026)

**O motor pago que já estava pago.** A `GOOGLE_APPLICATION_CREDENTIALS` está no
`.env` desde sempre, a API está habilitada, e a conta responde 30 vozes
Chirp3-HD em pt-BR — 16 masculinas, 14 femininas. Nenhum cadastro novo.

Gerado por `python -m pipeline.vozes --google-masculinas --kokoro`, que é o
primeiro gerador reutilizável desta pasta: as duas levas anteriores foram
feitas com script descartável, e o nivelamento de loudness dependia de eu
lembrar. Agora é obrigatório e automático — **−18 LUFS em todas**.

Trecho: cena 2 do video-03, escolhido porque contém `manhã` e `água`, as duas
palavras que o Samuel apontou como erradas no Kokoro. A pergunta desta leva não
é "qual voz é mais bonita", é **"qual acerta o defeito que eu ouvi"**.

### Como ouvir

`google-chirp3/contato.wav` — as 17 amostras numa sequência só, cada uma
anunciada por número na voz atual (`pm_santa`), que fica óbvio ser o locutor.
Fone, à noite, no volume de dormir. Os arquivos individuais estão ao lado, para
reouvir uma específica.

Não é prova cega, e de propósito: com 17 candidatas o sorteio atrapalharia mais
do que protege. A prova cega vem na leva seguinte, entre as 3 ou 4 finalistas
que você apontar, contra a Kokoro atual, com trecho de 90 s.

### O ritmo está casado — de propósito

**Todas as amostras levam a mesma pausa de 1,2 s entre frases**, que é a do
plano do video-03. Sem isso a comparação seria desonesta: o Kokoro sai a 102 ppm
porque tem a pausa, e o Chirp3-HD cru sai a ~170 porque não tem nenhuma. Lado a
lado, o que se julgaria seria o ritmo — que é **parâmetro nosso, igual para
todos** — em vez do que está em disputa, que é a voz.

Com a pausa aplicada em todas:

| | ppm |
|---|---|
| `kokoro pm_santa` 0,75 (atual) | 102 |
| Chirp3-HD mais lenta (`Achird`) | 115 |
| Chirp3-HD mais rápida (`Schedar`) | 142 |
| referência Dreamoria | 128 |
| referência History at Night | 180 |

A dispersão que sobra é o ritmo próprio de cada voz, e essa é diferença real.
Vale notar que **as Chirp3-HD caem em cima do Dreamoria**, a referência de
narrativa que funciona — enquanto nós estamos 26 ppm abaixo dela.

### Resultado

_(preencher: números preferidos, e por quê)_

### Resultado — 05/09/2026

**Espaçamento: tratamento 3, `[pause]` entre frases.** O Samuel rejeitou tanto o
`[pause short]`, que some, quanto o 1,2 s inserido do Kokoro, que ele descreveu
como "o espaçamento está grande". Estava mesmo: no Chirp3-HD o 1,2 s se soma aos
~0,45 s que o modelo já faz no ponto e vira **1,6 s efetivos**.

**Vozes aprovadas em pt-BR (10 de 16):** Algenib (preferida), Algieba, Charon,
Enceladus, Iapetus, Orus, Rasalgethi, Sadachbia, Umbriel, Zubenelgenubi.
Descrição dele: *"não são tão caricatas, mas são muito boas"*.

**Vozes aprovadas em inglês (4):** Algenib, **Algieba** (preferida, "muito
boa"), Enceladus, Sadachbia — e o veredito geral foi que **as inglesas são
"muito melhor do que as em português"**. Faz sentido: inglês é o locale primário
do Chirp3-HD.

### A hierarquia que saiu daí

O tratamento 3 sozinho, aplicado a todas as fronteiras, dava 163 ppm — rápido
demais. A correção não foi aumentar a pausa (ele já tinha reprovado isso), foi
**usar a estrutura que o roteiro já tem**:

| fronteira no roteiro | marca |
|---|---|
| frase (`.` `!` `?`) | `[pause]` |
| respiro (`...`) | `[pause]` |
| **parágrafo (linha em branco)** | **`[pause long]`** |

Medido nas cenas 1–3 do roteiro real do video-03, voz Algenib: **127 ppm**,
contra 128 do Dreamoria. As amostras estão em `hierarquia/`.

Nenhum parâmetro novo no `plano.json` — a marcação sai de
`pipeline/vozes.py::marcar_roteiro`.
