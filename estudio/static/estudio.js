// Dispara um estágio do pipeline (POST) e acompanha o log ao vivo via
// Server-Sent Events. Vanilla JS em vez de uma extensão SSE do htmx — é uma
// única interação, não vale vendorizar mais um arquivo por isso.
//
// Devolve uma Promise que só resolve quando o estágio termina (evento
// "done") — quem chama e precisa fazer algo DEPOIS (tipo recarregar um
// player de áudio) usa `await rodarEstagio(...)`, não só dispara e esquece.
function rodarEstagio(slug, estagio, botaoId, logId, extras) {
  // `null` = o coletor barrou (ex.: gasto não confirmado) e já escreveu no log.
  // Não confundir com `undefined`, que é chamada sem extras e é válida.
  if (extras === null) return Promise.resolve(false);

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
        resp.text().then((corpo) => {
          // FastAPI devolve {"detail": "..."} — mostrar o texto, não o JSON cru.
          let msg = corpo;
          try { const j = JSON.parse(corpo); if (j.detail) msg = j.detail; } catch (_) {}
          log.textContent = `erro ao iniciar (${resp.status}): ${msg}`;
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


// Lê os controles que existirem para um estágio e monta o corpo do POST. Os ids
// seguem `campo-estagio`, então o mesmo coletor serve para todos e a tela pode
// ganhar campo novo sem tocar aqui. O que o estágio não declarar em `campos`
// nem aparece no HTML, e o servidor ignora de todo jeito.
function extrasDe(nome) {
  const extras = {};
  const campo = (prefixo) => document.getElementById(`${prefixo}-${nome}`);

  const forcar = campo("forcar");
  if (forcar && forcar.checked) extras.forcar = "true";

  for (const p of ["cena", "modelo", "jobs"]) {
    const el = campo(p);
    if (el && el.value) extras[p] = el.value;
  }

  // Confirmação de gasto: sem o marcador, nem envia — mas a guarda que vale é
  // a do servidor (ver pipeline_run.rodar), esta só evita a ida à rede.
  const confirmo = campo("confirmo");
  if (confirmo) {
    if (!confirmo.checked) {
      document.getElementById(`log-${nome}`).textContent =
        "este estágio gasta na fal.ai — marque 'confirmo o gasto' antes de rodar.";
      return null;
    }
    extras.confirmo_custo = "sim";
  }
  return extras;
}


// Dispara uma SEQUÊNCIA de estágios. Mesma mecânica de SSE do estágio avulso —
// o servidor escreve tudo num log só e marca cada passo — então o front só
// precisa apontar para outra URL.
function rodarSequencia(slug, nome, id) {
  const botao = document.getElementById(`btn-${id}`);
  const log = document.getElementById(`log-${id}`);
  const confirmo = document.getElementById(`confirmo-seq-${nome}`);

  if (confirmo && !confirmo.checked) {
    log.textContent = "esta sequência inclui etapa que gasta na fal.ai — " +
                      "marque 'confirmo o gasto' antes de rodar.";
    return Promise.resolve(false);
  }
  const corpo = new FormData();
  if (confirmo) corpo.append("confirmo_custo", "sim");

  log.textContent = "";
  botao.disabled = true;
  botao.textContent = "rodando...";

  return fetch(`/projetos/${slug}/sequencias/${nome}/rodar`, { method: "POST", body: corpo })
    .then((resp) => new Promise((resolve) => {
      if (!resp.ok && resp.status !== 409) {
        resp.text().then((c) => {
          let msg = c;
          try { const j = JSON.parse(c); if (j.detail) msg = j.detail; } catch (_) {}
          log.textContent = `erro ao iniciar (${resp.status}): ${msg}`;
        });
        botao.disabled = false; botao.textContent = "rodar sequência";
        resolve(false); return;
      }
      const fonte = new EventSource(`/projetos/${slug}/estagios/${nome}/logs`);
      fonte.onmessage = (ev) => {
        log.textContent += ev.data + "\n";
        log.scrollTop = log.scrollHeight;
      };
      fonte.addEventListener("done", (ev) => {
        log.textContent += ev.data === "0"
          ? "\n[sequência concluída]\n"
          : `\n[PAROU — código ${ev.data}. Veja acima em que passo]\n`;
        fonte.close();
        botao.disabled = false; botao.textContent = "rodar de novo";
        resolve(ev.data === "0");
      });
      fonte.onerror = () => {
        fonte.close(); botao.disabled = false;
        botao.textContent = "rodar sequência"; resolve(false);
      };
    }))
    .catch((e) => {
      log.textContent = `erro de rede: ${e}`;
      botao.disabled = false; botao.textContent = "rodar sequência";
      return false;
    });
}
