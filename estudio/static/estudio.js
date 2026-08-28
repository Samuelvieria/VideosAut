// Dispara um estágio do pipeline (POST) e acompanha o log ao vivo via
// Server-Sent Events. Vanilla JS em vez de uma extensão SSE do htmx — é uma
// única interação, não vale vendorizar mais um arquivo por isso.
//
// Devolve uma Promise que só resolve quando o estágio termina (evento
// "done") — quem chama e precisa fazer algo DEPOIS (tipo recarregar um
// player de áudio) usa `await rodarEstagio(...)`, não só dispara e esquece.
function rodarEstagio(slug, estagio, botaoId, logId, extras) {
  const botao = document.getElementById(botaoId);
  const log = document.getElementById(logId);
  log.textContent = "";
  botao.disabled = true;
  botao.textContent = "rodando...";

  const corpo = new FormData();
  for (const [k, v] of Object.entries(extras || {})) corpo.append(k, v);

  return fetch(`/projetos/${slug}/estagios/${estagio}/rodar`, { method: "POST", body: corpo })
    .then((resp) => new Promise((resolve) => {
      if (resp.status === 409) {
        log.textContent = "já tem uma execução rodando para este estágio — acompanhando...\n";
      } else if (!resp.ok) {
        resp.text().then((detalhe) => {
          log.textContent = `erro ao iniciar (${resp.status}): ${detalhe}`;
        });
        botao.disabled = false;
        botao.textContent = "rodar";
        resolve(false);
        return;
      }

      const fonte = new EventSource(`/projetos/${slug}/estagios/${estagio}/logs`);
      fonte.onmessage = (ev) => {
        log.textContent += ev.data + "\n";
        log.scrollTop = log.scrollHeight;
      };
      fonte.addEventListener("done", (ev) => {
        log.textContent += `\n[finalizado — código ${ev.data}]\n`;
        fonte.close();
        botao.disabled = false;
        botao.textContent = "rodar de novo";
        resolve(ev.data === "0");
      });
      fonte.onerror = () => {
        fonte.close();
        botao.disabled = false;
        botao.textContent = "rodar";
        resolve(false);
      };
    }))
    .catch((e) => {
      log.textContent = `erro de rede ao iniciar: ${e}`;
      botao.disabled = false;
      botao.textContent = "rodar";
      return false;
    });
}
