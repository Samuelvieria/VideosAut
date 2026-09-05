---
projeto: Canal de Sono Automatizado
assunto: avaliação do "Guia Mestre: Canais de IA no YouTube"
data: 2026-09-05
fonte: docs/consultas/brutas/guia-canal-ia-qwen.md (gerado pelo Qwen)
---

# O guia genérico de canal de IA, medido contra o que já sabemos

O Samuel mandou este guia em 04/09 pedindo revisão do projeto à luz dele. A
conclusão curta: **ele descreve um produto diferente do nosso**, e seguido ao pé
da letra destruiria o vídeo de sono. Mas tem quatro itens que valem, e um deles
encaixa direto numa coisa que já produzimos.

Isto não é desprezo pela fonte. É o que `docs/verificacao.md` manda fazer com
qualquer conselho: perguntar sobre qual produto ele foi escrito.

---

## Para que produto o guia foi escrito

Vídeo de 8 a 12 minutos, em tecnologia/finanças/autoajuda, onde a métrica é
**clique e permanência**, e o inimigo é o espectador desistir.

O nosso é de 65 a 170 minutos, e **o sucesso é o espectador parar de assistir
porque dormiu**. Quase toda mecânica se inverte.

| o guia manda | nós, medido |
|---|---|
| mudança visual a cada 3–5 s | cena de ~90 s com pan de 1 px/frame |
| SFX de *whoosh*, *riser*, *hit* "para dopaminar" | ambiente contínuo, sem nenhum evento |
| legenda dinâmica queimada estilo Hormozi | legenda **soft**; texto na tela é contraproducente |
| 8–12 minutos | 65–170 min ([mercado.md](../mercado.md) §2) |
| gancho contraintuitivo em 0–30 s | *"Boa noite. Se acomode."* |
| CTA pedindo comentário | nada que peça ação |
| variar tom para dúvida/empolgação | dinâmica plana é requisito do formato |

**Cada linha da direita foi medida ou julgada de ouvido neste projeto.** Nenhuma
é preferência.

---

## Onde o guia está factualmente errado

**"ElevenLabs: a única opção viável."** Falso, e caro. Medido em 05/09: o Google
Chirp3-HD dá 30 vozes pt-BR — 16 masculinas, 14 femininas — por **R$ 21/mês** na
cadência quinzenal bilíngue, contra R$ 505 do ElevenLabs. E a credencial já
estava no `.env`. Ver [tts-provedores.md](../tts-provedores.md).

**"RPM de US$ 5 a 20 por mil views."** Isso é faixa de tecnologia e finanças.
Conteúdo de sono tem **RPM baixo e watch time alto** — o modelo econômico é
outro, e confundir os dois leva a decidir errado sobre formato.

**"Se o CTR ficar abaixo de 4% em 24 h, troque a miniatura."** Benchmark de
nicho de curiosidade. Em sono, boa parte do tráfego é busca com intenção já
formada, e o CTR se comporta diferente. Trocar miniatura por causa desse número
seria agir sobre um limiar emprestado.

**"Roteirista nativo ou IA + revisor."** Aqui concordamos com ele e o
`CLAUDE.md` já é mais rígido: tradução publicada é obra protegida, e o roteiro
em inglês é **reescrito**, nunca traduzido.

---

## Os quatro itens que valem

### 1. Teste A/B nativo de até 3 miniaturas — e nós já geramos exatamente 3

É o encaixe mais direto de todo o pack. O `pipeline/s5b_thumbs.py` produz **três
candidatas** de três cenas diferentes, com folha de contato, desde 04/09. Até
agora a folha servia para o Samuel **escolher uma**. O YouTube deixa subir as
três e decidir por dado.

O recurso vem junto com a etapa 3 de "Recursos avançados"
([videos/README.md](videos/README.md) §1), que também precisa ser ativada.

**Mudança de uso, não de código.**

### 2. Aba Comunidade com enquetes

O guia afirma que o YouTube entrega enquete da aba Comunidade na home de
**não-inscritos**, e que é a ferramenta orgânica mais forte hoje para canal sem
rosto. Não confirmei essa afirmação e ela não deve ser tratada como fato — mas o
custo de testar é quase zero, e nós temos material de sobra: as imagens
descartadas de cada vídeo, e as três miniaturas.

Enquete plausível: *"qual dessas duas noites você quer ouvir primeiro?"* com
duas imagens. Serve de teste de tema **antes** de escrever 6.375 palavras.

### 3. Ler o gráfico de retenção toda semana

Já temos a ferramenta (`pipeline/s7_metricas.py`, somente leitura) e ela já sabe
que em sono o que importa é **duração absoluta**, não percentual. O que falta é
o hábito. O video-02 está publicado desde 03/09 e **ninguém leu os números
ainda** — e essa é a pergunta central do projeto inteiro.

### 4. Documentar procedimento

O guia manda criar SOPs no Notion. Nós já fazemos melhor, em `CLAUDE.md`, nas
skills e nos `README` de cada estágio — e versionado junto com o código que os
executa. Nada a fazer; registrado para não parecer omissão.

---

## O que NÃO adotar, e por quê

- **Shorts como isca.** Plausível em geral, mas o espectador de sono está
  deitado no escuro às 23h — não está rolando Shorts. E um Short exige corte
  rápido, que é o oposto do que o canal ensina o algoritmo a associar a nós.
  Não é "não", é "não antes de a Fase 0 fechar".
- **Afiliados de ferramenta de IA na descrição.** Traz o público errado e
  contradiz o tom. O sono monetiza por watch time e, mais tarde, por produto
  próprio (faixa longa, app), não por link de SaaS.
- **Venda do canal por 24–36× o lucro.** Especulação sobre múltiplo de
  marketplace. Irrelevante com dois vídeos publicados.
- **"Velocidade vence perfeição."** É o conselho mais perigoso do pack para
  este projeto. O `CLAUDE.md` já registra que volume alto com formato idêntico
  é o sinal de risco número um, e a pesquisa de mercado mostrou que os dois
  canais de referência publicam **um vídeo a cada cinco semanas**.
