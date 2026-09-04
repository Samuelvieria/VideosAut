---
projeto: Canal de Sono Automatizado
assunto: o que foi feito na sessão autônoma da madrugada de 04/09/2026
data: 2026-09-04
---

# A noite de 04/09

Samuel foi dormir e autorizou ~3 h de trabalho autônomo, com uso do Gemini
(`agy`) para revisão e delegação. Isto é o relatório.

Tudo está commitado e no `main`. Nada foi publicado no YouTube, nada foi gasto
em API paga, e nenhum arquivo seu foi sobrescrito.

---

## O canal se mexeu durante a noite

Quando comecei, o video-02 tinha **4 views**. Ao terminar, tem **253 views e 13
likes**.

Não vou vender isso como validação, porque não é:

- 253 continua sendo pouco, e a origem do tráfego ainda não dá para ver
- **retenção continua sem dado** — o Analytics atrasa até 48 h, e retenção é a
  única coisa que responde a pergunta do projeto
- 13 likes em 253 views é 5,1%, acima do típico de 2–4% — mas em amostra desse
  tamanho isso é ruído, não sinal

O que muda de verdade: a base do argumento "não temos dado nenhum" tinha 4
views. Agora tem movimento. **Vale voltar ao `s7_metricas` daqui a 24–48 h**,
quando a curva de retenção existir. É ela, e não a contagem de views, que diz
se o produto presta.

---

## O resumo em cinco linhas

Seis tarefas concluídas, todas do `docs/estado-e-direcao.md` §5 e do
`docs/mercado.md` §8. O estúdio agora **fecha o ciclo**: cria projeto, roda os
sete estágios, gera thumbnail. As lições de prompt que estavam em documento
viraram **recusa em código**. E delegar auditoria ao Gemini achou **sete erros
meus**, dos quais quatro eu não teria encontrado sozinho.

---

## O que foi feito

| | tarefa | onde |
|---|---|---|
| T1 | Personas carregam estética, e cue ruim é recusado | `estudio/db/personas.py` |
| T2 | Criar projeto pelo estúdio, a partir de uma persona | `estudio/db/projetos.py` |
| T3 | Estágio de thumbnail com as três candidatas | `pipeline/s5b_thumbs.py` |
| T4 | Título, tags e descrição do video-02 revisados | `fase0/video-02/metadados-revisados.md` |
| T6 | Amostras de ritmo de voz | `fase0/_vozes-candidatas/` |
| — | Auditoria da noite inteira pelo Gemini | commit `2d364ad` |

**T5 não foi feita**, e é a decisão que espera você — ver o fim.

---

## O que exige decisão sua

### 1. O video-03 vai para 75 min?

Ele está planejado com **30**. O mercado não tem um só caso de sucesso perto
disso: a faixa é 65–170 min. Mudar agora custa reescrever o roteiro; depois de
produzido, custa refazer tudo.

Se for, o roteiro precisa de **~7.650 palavras** (75 × 102 ppm medidos). Hoje
tem 2.157. Não é esticar o que existe — é escrever outro.

Não escrevi por conta própria: sete mil palavras de narrativa do seu canal é
decisão de gosto, e o `voz.md` foi extraído do *seu* texto aprovado, não do meu.

### 2. Ritmo da narração

Em `fase0/_vozes-candidatas/` tem quatro amostras do mesmo trecho:

| arquivo | ppm |
|---|---|
| `kokoro-speed060-atual.wav` | 123 |
| `kokoro-speed075.wav` | 152 |
| `kokoro-speed090.wav` | 195 |
| `kokoro-speed100-pausa.wav` | 205 |

A pergunta é uma só: **lentidão por esticar a fala, ou por pausar entre
frases?** A 0,60 o Kokoro estica vogal e consoante junto. A 1,00 com pausa
crescente a articulação fica natural e a lentidão vem do silêncio.

Ouça no fone, à noite, no volume de dormir.

### 3. Título e tags do video-02

Está pronto para colar em `fase0/video-02/metadados-revisados.md`. Não apliquei
porque nosso OAuth é só leitura.

### 4. Capítulos — ficou em aberto

O `monetizacao.md` diz não usar (a barra convida a pular). O Gemini levantou o
contrário, e o argumento é bom: capítulo deixa o **recorrente** achar onde
adormeceu, e recorrente é o único ativo real do nicho. Nenhum lado tem dado.

---

## O que a noite descobriu e contraria decisões nossas

**Nenhuma das duas referências tem cauda de ambiente.** A última legenda do
History at Night cai aos 75 de 75 min; a do Dreamoria, aos 169 de 169. As duas
narram até o fim. Nossa cauda de 9 min é invenção nossa, e o nosso "vídeo de 41
min" é um vídeo de **32 min com 9 de chuva**.

**Eles não desaceleram — só nós.** Medido por terço: −4,1% e −1,0%. Praticamente
reta. Nosso `FATOR_PAUSA` vai de 1,0 a 1,6 de propósito, e isso nunca foi
comparado com nada.

**Em pt-BR, o termo é ocupado por conteúdo infantil, e "adultos" não resgata.**
Busquei cinco termos: `história para dormir adultos` devolve Cinderela, Masha e
o Urso e Sapo Zé. E `audiolivro para dormir` traz Tolstói e Camus **em
espanhol**, sinal de que o segmento adulto narrado em português é fino o
bastante para o algoritmo buscar fora do idioma.

---

## Os erros meus que apareceram, e como

Registro porque o `docs/verificacao.md` existe para isso.

**Quatro achados pelo Gemini que eu não teria encontrado:**

1. **Validei três campos que não chegavam ao pipeline.** A persona guardava
   `resolucao`, `paleta` e `luz`, e o estúdio validava tudo — mas o
   `s3_imagens` usa constante chumbada e só lê `estilo_base`. Campo validado
   sem efeito é pior que campo ausente: dá impressão de configurar algo.
2. **Deixei `duracao_min * 80`** na meta de palavras do roteiro gerado — o
   número que eu mesmo corrigi para 102 três commits antes, na mesma sessão.
3. **Tirei "eles rodam perto do normal" de médias globais** sem testar se eles
   desaceleram. Era testável. Testei, e a conclusão se sustentou — mas por
   sorte, não por método.
4. **Generalizei "casos de sucesso produzem majoritariamente fracassos"** de um
   canal só. No History at Night a dispersão é 6,7×, não 350×.

**Três achados meus, olhando o resultado em vez de confiar que funcionou:**

5. Escrevi as regex de validação num heredoc não-raw, e **`\b` em Python é
   backspace**, não fronteira de palavra. Três das quatro regras viraram
   caractere invisível e aceitavam tudo. Só a primeira funcionava.
6. A primeira guarda de resolução **rejeitava 1280×720**, a nossa própria
   resolução de produção — modelei errado, achando que o render escala direto
   para 1920×1080, quando ele escala ×2 e recorta.
7. A posição fixa do texto da thumbnail **caía em cima da multidão** na variante
   C. Só apareceu olhando a folha de contato.

E um que quase custou caro: o estágio de thumbnail ia **sobrescrever as três
feitas à mão, incluindo a `thumb_B` publicada**. Agora ele se recusa a
sobrescrever arquivo que não foi ele que gerou.

---

## Como o Gemini foi usado

Pelo `agy` (Antigravity CLI), modelo `gemini-3.1-pro-high`, três vezes:

1. Revisão adversarial do validador de estética — achou 4 buracos
2. Crítica estratégica da proposta de título e tags — achou a contradição
3. Auditoria da noite inteira — os 4 achados acima

Nunca recebeu `.env`, chave, nem credencial. O método foi uma **caixa de saída
isolada**: copio para uma pasta só o que decidi enviar, e ele só enxerga
aquilo. Protocolo em `docs/consultas/README.md`.

Duas vezes ele errou um fato e eu peguei porque tinha a medição — disse que a
regra de resolução era 1024×576, quando é 1280×720 desde 02/09. Ele leu o
número velho **na nossa skill**, que estava desatualizada. Ou seja: a revisão
achou deriva de documentação de lambuja.

**A regra que usei:** revisão dele é entrada, não veredito. Onde ele discordou
de medição nossa, a medição ganhou. Onde ele apontou algo testável, eu testei
em vez de aceitar ou rejeitar pela prosa.

---

## O que continua bloqueado por você

- Escrever no YouTube (título, tags): OAuth é `youtube.readonly`
- Fish Audio e ElevenLabs: precisam de cadastro
- Gerar imagens na fal.ai: gasta dinheiro, e eu não gasto o seu dormindo
- `s1_roteiro.py` / `s6_upload.py`: proibidos até 2–3 vídeos publicados
- Workstation: a máquina não está aqui

O PC continua ligado. Ainda há trabalho desbloqueado na lista.

---

# Segunda parte — a noite de 04/09

O Samuel ouviu a narração do video-03 e disse: *"a ênfase nas sílabas está
errada"*. Isso virou o trabalho da noite.

## O achado, e o que ele implica para o vídeo já publicado

**`speed` abaixo de 0.85 destrói o acento tonal do Kokoro.** Teste pareado,
mesma palavra, mesma voz, só a velocidade muda:

| speed | pico de F0 na sílaba tônica |
|---|---|
| 0.60 | 1 de 6 |
| 0.70 | 0 de 6 |
| 0.80 | 1 de 6 |
| **0.85** | **4 de 6** |
| 1.00 | 4 de 6 |

Abaixo de 0.85 a curva de altura só decai ao longo da palavra, sem pico nenhum.
Como em português a tônica se marca também por subida de altura, **toda palavra
soa acentuada na primeira sílaba**.

**E o video-02 foi gerado a 0.60.** Ou seja: o vídeo que está no ar tem o mesmo
defeito. Você o aprovou de ouvido na época — talvez não incomode ali, talvez
incomode agora que o ouvido está calibrado. **É decisão sua**, e ela tem custo:
regerar a narração implica refazer o render e substituir o vídeo publicado,
perdendo as views e o histórico. Eu não faria isso sem você mandar.

## O que mudou no pipeline

- `speed` do video-03 subiu para **0.85**, e a lentidão passou a vir da pausa —
  que agora é **parâmetro do projeto** (`voz.pausa_respiro_s`,
  `voz.pausa_paragrafo_s`), não constante global. O video-02 não tem essas
  chaves e continua exatamente como estava.
- **Custo real:** a pausa tem retorno decrescente. O video-03 cai de 68 para
  ~52 min. Nem 6× a pausa passa de 57. Se a duração alvo for alta, a resposta é
  mais **texto**, não mais silêncio.
- A marca de idempotência do `s2_tts` passou a ser **por cena**. Antes usava o
  arquivo inteiro do roteiro como entrada, então mudar uma palavra numa cena
  regerava as 38 — 25 minutos de CPU por uma frase.

## O que mais foi feito

- **`s2b_revisar`** — página local com um player por cena e o texto ao lado, em
  frases numeradas. Clicar numa frase copia "cena N, frase M". Serve para você
  apontar o defeito exato em vez de descrevê-lo.
- **Sequências no estúdio** — `mecanica` (não gasta) e `completa` (gasta),
  rodando os estágios na ordem certa e **parando no primeiro erro**.
- **Revisão histórica do roteiro** pelo Gemini: achou um anacronismo real
  (tesoura de eixo é romana, não grega) e errou no ponto grande (afirmou que
  faróis queimavam lenha, não óleo — a evidência sobre o Farol de Alexandria
  diz o contrário). Detalhes no `fase0/video-03/README.md`.

## O `preflight`, e o bug que ele achou na primeira execução

Escrevi um comando que confere o projeto **antes** de gastar dinheiro ou tempo:
`python -m pipeline.preflight fase0/video-03`. Ele virou o primeiro passo das
duas sequências do estúdio.

Confere roteiro contra plano (contagem e títulos), piso de `speed`, duração
projetada contra o alvo e contra o piso do mercado, cue proibido no
`estilo_base` **e no prompt de cada cena**, `obra` acentuada, cena sem prompt,
formato do `ambiente`, cena sem pista de luz, e o custo em reais.

**Na primeira execução ele achou um bug meu, e grave.** Eu tinha escrito o campo
`ambiente` das 18 cenas novas do video-03 como **texto** — "vento nas frestas,
mar ao longe" — quando ele é um **dicionário de níveis de mixagem**
`{mar, chuva, fogo, vento, abafado}`. O `s5_render` faz `cfg.get("mar")` e teria
quebrado no meio do render. Convertidas as 22 cenas e validadas: os perfis geram
estéreo com as camadas certas.

Depois mandei o Gemini auditar o próprio preflight — buraco em rede de segurança
é pior que não ter rede. Ele achou cinco, todos corrigidos, sendo o pior este: a
ferramenta que existe para evitar crash **crashava** com `ZeroDivisionError` se
`voz.speed` faltasse.

## O erro de método que se repetiu quatro vezes

Antes de achar a causa, fiz quatro medições que não serviram — e todas do mesmo
jeito: mediram algo **correlacionado** com tonicidade em vez de tonicidade.
Está registrado como o modo de falha nº 6 em [verificacao.md](verificacao.md).

O que funcionou foi teste **pareado**: mudar uma variável só. E isso só ficou
possível depois de eu conseguir mexer no fonema direto, envolvendo o `g2p` do
Kokoro. Antes disso eu comparava palavras diferentes e chamava de experimento.

---

## Estado ao fim da noite

- **Áudio do video-03**: regerando a `speed 0.85`, ~52 min. Quando terminar,
  rode `python -m pipeline.s2b_revisar fase0/video-03` e abra
  `fase0/video-03/audio/revisar.html`.
- **Estúdio**: 8 estágios, 2 sequências, criação de projeto, preflight. Testado
  de ponta a ponta — 9 telas respondem, 5 guardas barram.
- **video-03**: passa no preflight. 39 cenas, 38 prompts escritos, ambiente
  configurado, custo estimado de **R$ 0,96** (R$ 2,41 com retentativa).

### O que decide o próximo passo

**Ouça e diga se a ênfase melhorou.** Se sim, o piso de 0.85 fica valendo e o
video-03 sai com ~52 min. Se não, o problema é outro e a página de revisão
serve para você apontar a cena e a frase.

E fica de pé a pergunta da duração: 52 min contra o piso de 65 do mercado.
Fecha-se com **mais texto**, não com mais silêncio — a pausa tem retorno
decrescente e nem 6× o padrão passa de 57 min. São ~2.000 palavras a mais, e eu
não as escrevi porque você ainda não ouviu o que existe.
