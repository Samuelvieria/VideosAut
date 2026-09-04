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
