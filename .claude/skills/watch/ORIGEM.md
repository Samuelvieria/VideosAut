# Origem desta skill

Copiada de <https://github.com/bradautomates/claude-video> em 05/09/2026, a
pedido do Samuel. **MIT** (ver `LICENSE-upstream`), autor Bradley Bonanno.

Vendorizada no repositório em vez de instalada em `~/.claude/skills/` porque o
projeto roda em duas máquinas (Mac e workstation) e o que está no git chega nas
duas. São 128 KB.

## Como usamos aqui

Sem chave de Whisper. O `--no-whisper` usa as legendas nativas que o `yt-dlp`
baixa — é o que já fazíamos à mão em `docs/consultas/videos/`, e para vídeo de
YouTube com legenda automática dá no mesmo. O que a skill acrescenta e nós não
tínhamos é **os frames**: em vídeo de tutorial, metade da informação está na
tela, não na fala.

Se um dia quisermos vídeo sem legenda nativa, aí sim precisa de `GROQ_API_KEY`
ou `OPENAI_API_KEY` em `~/.config/watch/.env`.

## Atualizar

`git clone --depth 1` do repositório acima e copiar `skills/watch/` por cima.
Não editar os scripts aqui: divergir do upstream cria manutenção que ninguém
pediu.
