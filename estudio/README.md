# Estúdio

Interface web local para o pipeline — não é o pipeline. Roda:

```bash
python -m uvicorn estudio.main:app --reload --port 8000
```

Abrir http://localhost:8000/projetos

## Regra de separação (não quebrar isso)

`estudio/` **pode** importar de `pipeline/` (`pipeline.comum`, `pipeline.config`).
`pipeline/` **nunca** importa de `estudio/`. Os estágios continuam rodáveis sozinhos
por linha de comando (`python -m pipeline.sN_xxx ...`), sem saber que essa interface
existe — o app só os invoca via subprocesso (`estudio/services/runner.py`), nunca por
import direto de `main()`.

Motivo prático, não só estético: `pipeline.comum.erro()` faz `raise SystemExit(1)`.
Se um estágio fosse importado e chamado dentro do processo do servidor, um erro de
estágio derrubaria o servidor inteiro. Subprocesso isola isso como só um código de
saída não-zero.

## O que existe

- Listagem somente-leitura de `fase0/video-*` (lê `plano.json` com
  `pipeline.comum.carregar_plano`), com preview de imagens/áudio/vídeo/legendas.
- Botão "rodar `s3_imagens --seco`" com log ao vivo via Server-Sent Events — grátis,
  não chama a API do fal.ai, existe para provar o mecanismo de log antes de ligar
  qualquer estágio pago/lento.
- CRUD de personas (`estudio/dados/personas.json`) — nome, descrição, voz por idioma
  (hoje só `pt`/Kokoro tem valores reais; `en` fica presente-mas-nulo até o projeto
  escolher um motor de voz em inglês).
- **Mixer de áudio** (`/projetos/{slug}/mixagem`) — ganho/reverb/lowpass do ambiente e
  os 4 parâmetros do ducking, editáveis por slider, salvos no bloco `mixagem` do
  `plano.json`. Botão "gerar preview" roda `s5_render --so-mix` (refaz só
  `build/mix.m4a`, segundos, não re-renderiza o vídeo) e toca o resultado num
  `<audio>`. Existe porque ninguém aqui consegue ouvir o áudio enquanto ajusta os
  filtros de ffmpeg às cegas — ver `.claude/skills/qualidade-producao-video/SKILL.md`.
- **Correções** (`/projetos/{slug}/correcoes`) — anotações de ajuste por cena ou
  gerais, com estado aberta/resolvida. Não dispara nada sozinho: é registro
  estruturado do que falta ajustar, pra não depender só do histórico de chat.

## Lições de produção

`.claude/skills/qualidade-producao-video/SKILL.md` acumula as técnicas de prompt de
imagem, mixagem e movimento de câmera que já causaram erro uma vez neste canal —
atualizar esse arquivo sempre que uma correção nova valer a pena não repetir no
próximo vídeo.

## O que NÃO existe aqui, de propósito

Nenhum botão de upload/publicação (`s6_upload.py` continua não existindo em lugar
nenhum). Nenhuma geração de roteiro por LLM ainda — isso é a próxima fase do roteiro
de continuação (fila de roteiros + rascunho via Claude API, **nunca** promovido a
produção sem edição e aprovação humana explícita: o gate fica em dois arquivos físicos
separados, `rascunho.md` vs `aprovado.md`, não numa flag de status). Ver
`CLAUDE.md` na raiz do repo para o porquê desse limite — é uma decisão travada do
projeto, não uma limitação técnica desta interface.

Disparo real dos estágios pagos/lentos (`tts`, `imagens` de verdade, `render`,
`legendas`), criação de projeto a partir de um roteiro aprovado, e o formato/modelo
de vídeo (hoje só existe um formato, "historinha 30min pixel art") também ficam para
as próximas fases.
