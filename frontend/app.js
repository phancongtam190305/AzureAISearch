const form = document.getElementById("search-form");
const answersEl = document.getElementById("answers");
const resultsEl = document.getElementById("results");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderAnswers(answers) {
  if (!answers?.length) {
    answersEl.className = "stack empty";
    answersEl.innerHTML = "Khong co answer nao duoc tra ve.";
    return;
  }

  answersEl.className = "stack";
  answersEl.innerHTML = answers
    .map(
      (answer) => `
        <article class="answer">
          <p>${escapeHtml(answer.text)}</p>
          <small>Score: ${Number(answer.score ?? 0).toFixed(3)}</small>
        </article>
      `
    )
    .join("");
}

function renderResults(items) {
  if (!items?.length) {
    resultsEl.className = "stack empty";
    resultsEl.innerHTML = "Khong tim thay ket qua.";
    return;
  }

  resultsEl.className = "stack";
  resultsEl.innerHTML = items
    .map((item) => {
      const caption = item.captions?.[0]?.text || item.content || "";
      const tags = (item.tags || []).map((tag) => `<span>${escapeHtml(tag)}</span>`).join("");
      const link = item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">Mo link</a>` : "";

      return `
        <article class="result">
          <div class="result-head">
            <div>
              <h3>${escapeHtml(item.title || "Khong co tieu de")}</h3>
              <p class="meta">${escapeHtml(item.category || "Uncategorized")}</p>
            </div>
            <strong>${Number(item.reranker_score ?? item.score ?? 0).toFixed(3)}</strong>
          </div>
          <p>${escapeHtml(caption)}</p>
          <div class="tags">${tags}</div>
          ${link}
        </article>
      `;
    })
    .join("");
}

async function runSearch(event) {
  event?.preventDefault();
  answersEl.className = "stack empty";
  resultsEl.className = "stack empty";
  answersEl.textContent = "Dang truy van...";
  resultsEl.textContent = "Dang tai ket qua...";

  const query = document.getElementById("query").value.trim();
  const mode = document.getElementById("mode").value;
  const top = document.getElementById("top").value;
  const params = new URLSearchParams({ q: query, mode, top });

  try {
    const response = await fetch(`/api/search?${params.toString()}`);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Search that bai");
    }

    renderAnswers(payload.answers);
    renderResults(payload.items);
  } catch (error) {
    answersEl.textContent = error.message;
    resultsEl.textContent = "Kiem tra .env, quyen Azure, hoac trang thai index.";
  }
}

form.addEventListener("submit", runSearch);
runSearch();

