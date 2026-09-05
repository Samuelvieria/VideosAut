---
projeto: Canal de Sono Automatizado
assunto: direção de roteiro — o que faz um episódio bom
data: 2026-09-05
leia-antes-de: escrever qualquer roteiro novo
irmão: docs/voz.md (o contrato mecânico: frase, termos banidos, verificação)
---

# Direção de roteiro

Este documento é lido **antes** de escrever. O [`voz.md`](voz.md) é lido
**enquanto** se escreve e para conferir no fim.

As regras abaixo saíram de erro cometido, não de teoria. Cada uma diz qual.

---

## 1. O sono vem da ENTREGA, não do enredo

História boa contada devagar faz dormir. História sem nada em jogo, contada
devagar, só é chata.

| acorda | não acorda |
|---|---|
| pico de volume, som súbito, vinheta | uma perda contada em voz baixa |
| quebra de ritmo, frase acelerada | um dilema moral, se a fala não muda de andamento |
| pedido de like, inscrição, comentário | tensão que se resolve sem grito |
| mudança brusca de ambiente entre cenas | um final que não consola |

**Um aviso de "isto pode acordar" sobre um ACONTECIMENTO quase sempre está
errado.** Vale sobre a entrega.

> **De onde veio.** No video-04 chegou uma lista de "trechos que podem acordar
> o ouvinte". Tratei a lista inteira como defeito e amaciei cinco passagens —
> quatro eram as melhores do roteiro. A pior troca: o camelo deixado para trás
> "com a cabeça erguida, olhando a gente ir embora" virou um consolo sobre ele
> conseguir levantar sozinho. Piorei a escrita para deixar mais segura.

## 2. Não fugir da ideia que a obra tem

**Filosofia não é o narrador ser sábio.** É o episódio encarar o que o assunto
levanta.

| entrar na ideia | tomar partido |
|---|---|
| a promessa é de 1915, o acordo de repartição é de 1916 | culpar um país |
| o narrador não sabia, e soube velho | julgar quem sabia |
| *"não senti raiva, e isso me incomoda"* | dizer o que o ouvinte deve sentir |

**Fato documentado com data é história. Atribuir culpa hoje é opinião.**

**O tell da covardia:** o narrador anunciar que está se recusando a contar
alguma coisa. Se aparecer "eu não vou falar disso", o problema já está na
página.

> **De onde veio.** O roteiro do video-04 passava duas horas sem dizer POR QUE
> quarenta pessoas atravessavam o deserto. Eu tinha posto Sykes-Picot "fora de
> quadro" e com isso tirei a razão da história. E a ideia mais interessante do
> material era justamente a cortada: o que é fazer o trabalho por uma causa
> cujos termos não te contaram.

**Verificação obrigatória:** o roteiro diz por que as pessoas fazem o que fazem?
Se não diz, falta o principal.

## 3. Toda cena precisa de gente, de um momento, e de uma chegada

Cena que descreve uma CATEGORIA não é história. "Camelo é assim", "Auda era
assim", "contava-se história à noite" — isso é documentário.

O conserto não é apagar o conteúdo factual, que costuma ser o melhor da
pesquisa. É **pendurá-lo num acontecimento**:

| era | virou |
|---|---|
| como se faz café no deserto | o homem de dois dedos que fazia o melhor café |
| Auda era um grande guerreiro | Auda parou atrás dele e disse "esse aí não chega" |
| contava-se sempre as mesmas histórias | a história de poço cujo fim ele não lembra |
| a espera é difícil | dois homens quase se mataram por uma corda |

E a cena deve **terminar onde o narrador não começou** — em coisa que ele viu,
nunca em aforismo. Um velho que diz "eu não sei o que fazer com isso" é mais
fundo que um que resolve.

> **De onde veio.** 14 das 69 cenas do video-04 tinham zero ou um acontecimento.

## 4. Duração tem DUAS alavancas, não uma

O ritmo não é constante do motor de voz. A marca `[pause]` cai em **fim de
frase**, então:

```
mais palavras       -> vídeo mais longo
frase mais curta    -> vídeo mais longo
```

| | marca a cada | ppm |
|---|---|---|
| video-03 | 6,8 palavras | 124–127 |
| video-04 | 9,7 palavras | 141 |

Projetar o video-04 pelos 127 do video-03 errou **11 minutos**. Use 135 para
estimar e trate o `duracoes.json` do `s2_tts` como o número real.

E frase curta é o que o contrato de voz já pede por outro motivo — as duas
regras empurram para o mesmo lado.

## 5. A estrutura do episódio

```
0:00 – 0:20   Entrada silenciosa. Sem vinheta. Uma frase de contexto.
0:20 – 1:30   Promessa: o que este episódio vai contar.
              <- A DECISÃO DO ESPECTADOR ACONTECE AQUI
1:30 – 20:00  Narrativa ativa.
20:00 – fim   Densidade decrescente. Repetição intencional de motivos.
[Final]       Sem CTA. Sem "se inscreva". Fade lento.
```

**A abertura promete; não lista ausências.** "Não tem batalha, não tem herói,
não tem ninguém salvando ninguém" é pedir desculpa pelo produto nos noventa
segundos em que a pessoa decide ficar.

O que funciona: dizer que existe uma coisa que o narrador não consegue
esquecer, e dizer qual é.

## 6. Política de conteúdo, que é regra de escrita e não de metadado

- **Originalidade.** Domínio público resolve direito autoral e **não** resolve
  monetização. Narrar texto que não escrevemos é o gatilho de conteúdo
  reutilizado, e ele vale para o canal inteiro.
- **Adulto.** Tema, léxico e ritmo de prosa adulta. Made for Kids desliga
  anúncio personalizado, comentário, notificação e memberships.
- **Nunca meditação guiada terapêutica.** Persona de IA dando conselho de saúde
  é categoria não monetizável. Narrativa, sempre.
- **Violência fora de quadro**, mas o CONFLITO dentro. Tema perturbador
  repetido sem narrativa coesa é gatilho; um dilema contado com calma não é.

## 7. Antes de mandar para produção

- [ ] Diz **por que** as pessoas fazem o que fazem?
- [ ] Alguma cena descreve categoria em vez de contar acontecimento?
- [ ] A abertura **promete** ou lista ausências?
- [ ] O narrador anuncia em algum ponto que se recusa a contar?
- [ ] O que foi amaciado por "pode acordar" era entrega ou era conteúdo?
- [ ] Passa no `voz.md`: mediana de 9 palavras, 57% até 10, zero banidos
- [ ] `python -m pipeline.preflight` limpo
