---
projeto: Canal de Sono Automatizado
assunto: quanto custa, quanto pode gastar, e o que decido sem perguntar
data: 2026-09-05
---

# Orçamento

Escrito em 05/09/2026, quando o Samuel propôs criar um cartão virtual e deixar
o acesso num arquivo para eu gerir as APIs.

**Recusei o cartão em arquivo e este documento é a alternativa.** O motivo está
no fim; o resto é o que ele pediu de verdade — que a produção não trave
esperando aprovação de dois reais.

---

## O que custa, medido

| | por vídeo de 2 h |
|---|---|
| imagens (fal.ai, ~74 a 1280×720) | **R$ 1,80** |
| com retentativa de 2,5× no pior caso | R$ 4,47 |
| voz pt-BR (Chirp3-HD, 87.691 caracteres) | **R$ 0** — dentro da faixa gratuita |
| voz + faixa em inglês (175.382 caracteres) | **R$ 0** — ainda dentro |
| legendas, ambiente, render | R$ 0 — tudo local |

**Gasto real do projeto até hoje: menos de R$ 5.** video-03 custou R$ 1,97 e
video-04 custou R$ 1,80, os dois de imagem.

### A faixa gratuita do Google, e a ressalva

1 milhão de caracteres por mês para Chirp3-HD, US$ 30 por milhão acima disso.
Isso dá **5 vídeos bilíngues por mês**, contra os 2 a 3 da cadência planejada.

**Continua sendo fonte secundária.** Três agregadores independentes dizem o
mesmo número e um deles é específico para Chirp 3 em vez de inferir da família
WaveNet, mas a página oficial não carrega inteira. Confirmar em
`console.cloud.google.com` → Faturamento → Relatórios, filtrando por Cloud
Text-to-Speech: se der R$ 0 com o consumo já feito, está confirmado.

**A marcação de pausa custa 19% a mais de caractere.** O roteiro do video-04 tem
73.858 caracteres e o enviado à API tem 87.691, porque cada `[pause]` e
`[pause long]` é cobrado. Irrelevante com a folga atual; deixaria de ser se a
cadência dobrasse.

---

## Teto e regras

**Teto: R$ 50 por mês.** Nos números acima isso compra 12 vídeos, o que é 4×
a cadência planejada. O teto existe para limitar erro, não para limitar
produção.

### O que eu faço sem perguntar

- Gerar imagens de um projeto que passou no `preflight` — até **R$ 10** por
  vídeo
- Regerar imagem individual reprovada de olho — sem limite prático, custa
  R$ 0,024 cada
- Gerar voz, legenda, ambiente e render — custa R$ 0
- Amostras de comparação (vozes, sons, avatares) — até **R$ 2** por rodada

### O que eu pergunto antes

- Qualquer coisa que passe de **R$ 10 numa tacada**
- **Assinatura de qualquer tipo** — nunca, sem exceção. Assinatura é
  recorrente e recorrente é diferente de gasto
- Regerar um lote inteiro de imagens já aprovado de olho
- Trocar de provedor pago

### O que eu nunca faço

- Criar conta, aceitar termo, ou fornecer dado de pagamento
- Usar `--dangerously-skip-permissions` em qualquer ferramenta

---

## O que precisa de você

- [ ] **Confirmar a faixa gratuita do Google** no console de faturamento — um
      minuto, e destrava o número mais importante deste documento
- [ ] **Ligar a recarga automática na fal.ai** (painel deles: recarrega US$ 10
      quando cair de US$ 5). Resolve o único caso em que a produção trava por
      dinheiro, e o cartão fica no provedor
- [ ] Nada mais. **Não há nada para assinar.**

---

## Por que não o cartão num arquivo

A troca é ruim: risco alto de vazamento em troca de quase nenhuma capacidade
nova.

**O risco é concreto neste projeto.** Um arquivo com cartão fica em texto puro
em duas máquinas, e um `git add -A` distraído põe no GitHub. E eu leio, todo
dia, conteúdo que não controlo: saída de outro modelo, legenda de vídeo do
YouTube, markdown baixado, página da web. Qualquer um pode trazer instrução
plantada, e cartão exposto não se rotaciona como chave de API se rotaciona.

**E não me daria capacidade nenhuma.** Eu não tenho navegador. Comprar crédito
ou assinar serviço é login e três cliques no painel — não é coisa que eu faça
mais rápido nem melhor.

O que travava não era falta de cartão. Era não saber até onde gastar sem
perguntar, e isso este documento resolve.
