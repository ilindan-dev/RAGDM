document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initChat();
});

function initTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const tabs = document.querySelectorAll(".tab-content");

  buttons.forEach((btn) => {
    btn.onclick = () => {
      buttons.forEach((b) => b.classList.remove("active"));
      tabs.forEach((t) => t.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(btn.dataset.tab + "-tab").classList.add("active");
    };
  });
}

function initChat() {
  const input = document.getElementById("input");
  const btn = document.getElementById("send");
  const chat = document.getElementById("chat");
  const loader = document.getElementById("loader");

  btn.onclick = async () => {
    const text = input.value.trim();
    if (!text) return;

    addMessage(chat, text, "user");
    input.value = "";

    loader.classList.remove("hidden");

    const result = await fakeApi(text);

    loader.classList.add("hidden");

    addMessage(chat, result.answer, "bot", result.meta);
  };
}

function addMessage(chat, text, type, meta = null) {
  const div = document.createElement("div");
  div.className = "message " + type;

  div.innerText = text;

  if (meta) {
    const m = document.createElement("div");
    m.className = "meta";
    m.innerText = meta;
    div.appendChild(m);
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function fakeApi(q) {
  return new Promise((res) => {
    setTimeout(() => {
      res({
        answer: "Дерево — связный граф без циклов.",
        meta: "Глава 2 · граф, дерево"
      });
    }, 1000);
  });
}