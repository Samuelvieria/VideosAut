# Seis vídeos mandados em 04/09/2026 — o que dava para usar

Transcrições em `.txt` ao lado, tiradas das legendas automáticas do próprio
YouTube via `yt-dlp` (não do whisper: mesma informação, minutos em vez de horas
de CPU). Os `.vtt` foram apagados depois de convertidos.

| vídeo | canal | dur | views | veredito |
|---|---|---|---|---|
| [7 Configurações que todo canal pequeno DEVE ativar](https://youtu.be/MBBisQmyld0) | Produccine | 16 min | 158 mil | **usar** — 6 ações concretas |
| [I BLEW UP a YouTube Channel in 24 Hours with AI](https://youtu.be/za2VyvLl5T0) | Jack Craig | 27 min | 1,06 M | **usar o método**, não o nicho |
| [I MONETIZED A Youtube Channel In 5 Days](https://youtu.be/Srar6q0qEC4) | Syrax | 6 min | 439 mil | **usar como contraprova** |
| [AI Voice Tutorial \| Generate and Clone](https://youtu.be/ylLwqY1_e_k) | Bad Decisions Studio | 15 min | 44 mil | pouco — é de 2023, sobre clonagem |
| [Use Elevenlabs FREE and UNLIMITED](https://youtu.be/7CxKvCn0Bxo) | Josephs AI | 5 min | 29 mil | **descartar** |
| [How to Edit AI Voice to Sound Realistic](https://youtu.be/fa9q3Il5-W0) | 4tuneGuide | 9 min | 252 mil | **não obtido** — 429 do YouTube |

---

## 1. As configurações de canal (Produccine) — o mais acionável dos seis

Seis coisas para conferir no Studio. Nenhuma delas depende de opinião.

1. **Palavras-chave do canal** (Configurações → Canal). Ajuda o YouTube a
   entender o tema antes de haver histórico. Estamos com dois vídeos: é
   exatamente a janela em que isso importa.
2. **Moderação de comentários rigorosa** + reter comentários com link. Canal de
   sono atrai spam de "cura da insônia" e link de golpe.
3. **Recursos avançados** (Configurações → Canal → Qualificação para recursos,
   3 etapas). Destrava miniatura personalizada, link externo na descrição, e
   — o que mais nos interessa — **teste A/B nativo de título e miniatura**.
4. **Capítulos automáticos: DESMARCAR.** O YouTube inventa a divisão sozinho e
   ela sai bagunçada. Isto **resolve metade da nossa pergunta em aberto sobre
   capítulos**: seja qual for a decisão de ter ou não, o automático é ruim e
   tem que sair.
5. **Padrão de envio: "não listado"**, não "público". Dá tempo de revisar tudo
   enquanto o vídeo processa.
6. **"Publicar no feed de inscrições e enviar notificações": MANTER MARCADA.**

> ### O item 6 contradiz uma decisão nossa, e o custo é real
>
> O `CLAUDE.md` manda subir **como `private`**, e a razão é boa (gate manual, e
> contorna a trava automática de projetos de API não auditados). Mas o vídeo
> recomenda **não listado**, e a diferença não é cosmética: é sabido que vídeo
> que sobe privado e só depois vira público pode **não disparar a notificação
> nem entrar no feed de inscritos** — a caixa é avaliada na publicação.
>
> Com 0 inscritos isso não custa nada. Com 5 mil, custa a primeira hora de
> tráfego, que é justamente o sinal que o algoritmo lê.
>
> **Não verificado.** Antes de mudar o `CLAUDE.md`, conferir no próximo vídeo:
> subir como não listado, publicar, e olhar se a notificação saiu.

---

## 2. O método do Jack Craig — estudar a estrutura, não copiar o conteúdo

O que ele faz de verdade, e que sobrevive à retórica de "24 horas":

> Abre um documento, pega os **3 vídeos mais vistos** de um canal que funciona,
> e anota **cena a cena**: duração, o que aparece, o texto falado, print. Só
> então extrai a **fórmula estrutural** — no caso dele
> `declarar → avaliar → isolar → processar → montar → revelar` — e aplica essa
> fórmula a **outro tema**.

A frase que justifica: *"YouTube does not reward duplicates of existing
channels."* É a mesma razão pela qual o `CLAUDE.md` proíbe prompt fixo e manda
usar banco de premissas com estruturas sorteadas — **este vídeo dá o método
para DERIVAR essas estruturas** de vencedores medidos, em vez de inventá-las.

Isso continua o que `docs/mercado.md` começou: lá medimos canal (duração,
cadência, título, ppm); aqui a medição desce para a **cena**.

### Os três critérios dele, e o que acontece com o terceiro

| critério | vale para nós? |
|---|---|
| **relatável universalmente** | sim, e forte — insônia não exige conhecimento de nicho |
| **gancho emocional** | sim, mas invertido: o dele é absurdo, o nosso é calma |
| **compulsão de completar** | **não, e de propósito** |

O terceiro merece atenção porque **nós o violamos deliberadamente**. A cena 1 do
video-03 diz, com todas as letras: *"Não precisa acompanhar até o fim. Se você
dormir no meio, a história continua sozinha."* Ele otimiza para o espectador
terminar; nós otimizamos para ele **dormir**, que é abandonar.

Isso não é erro nosso nem dele — é o que separa este nicho dos outros, e é a
razão pela qual conselho genérico de YouTube precisa ser filtrado antes de
entrar aqui. Também é por isso que `s7_metricas` mede **duração absoluta**, não
percentual.

---

## 3. A contraprova (Syrax): 10 milhões de views e monetização NEGADA

O método dele: baixar clipes de gente famosa, cortar em Shorts com ferramenta
automática, e — quando não vinham views — usar **GoLogin com proxy dos EUA**
para criar um perfil com IP novo e escapar de shadowban.

Resultado, nas palavras dele: 10 milhões de views em 40 dias, e a resposta do
YouTube foi **"não aprovado para monetização"**.

É a evidência mais direta que apareceu de que a política de conteúdo reutilizado
morde de verdade — e ela é do lado de quem tentou, não de quem alerta. Vale
guardar exatamente por isso.

A parte de proxy/IP é evasão de bloqueio de conta. Não entra aqui.

---

## 4 e 5. Os dois de voz — pouco aproveitável, e um deles perigoso

**"Use Elevenlabs FREE and UNLIMITED"** ensina a gerar um trecho curto no plano
gratuito e **clonar aquela voz em outro lugar** para não pagar. É contorno de
termo de uso, e clonar saída de um provedor para uso comercial é exatamente o
risco de licença que já tirou o XTTS-v2 deste projeto. Descartado.

**"AI Voice Tutorial"** é de 2023 e trata de clonagem por amostra. A única coisa
que sobrevive é sobre *speech-to-speech*: *"a slower speaking voice with clear
pronunciation gives more natural results"* e *"the AI will replicate the
performance of the voice you provide"*. Não usamos clonagem, então não se
aplica — e depois do Chirp3-HD (30 vozes pt-BR, sem clonagem) o assunto ficou
menos urgente.

**O de 252 mil views sobre deixar voz de IA realista não foi obtido** — o
YouTube devolveu 429 nas duas tentativas. É o mais relevante dos três de voz e
vale repetir depois: `yt-dlp --write-auto-subs --sub-langs en fa9q3Il5-W0`.
