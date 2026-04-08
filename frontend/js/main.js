document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initChat();
  initTrainer();
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

  const textBlock = document.createElement("div");
  textBlock.innerText = text;
  div.appendChild(textBlock);

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

function initTrainer() {
  const checkBtn = document.getElementById("check-answer-btn");
  const nextBtn = document.getElementById("next-question-btn");
  const answerInput = document.getElementById("trainer-answer");
  const questionBlock = document.getElementById("trainer-question");
  const resultBlock = document.getElementById("trainer-result");
  const statusBlock = document.getElementById("result-status");
  const percentBlock = document.getElementById("result-percent");
  const explanationBlock = document.getElementById("result-explanation");

  const questions = [
    {
      question: "Что называется полным графом?",
      result: {
        status: "partial",
        percent: 74,
        explanation:
          "Полный граф — это граф, в котором каждая пара различных вершин соединена ребром."
      }
    },
    {
      question: "Что называется путём в графе?",
      result: {
        status: "correct",
        percent: 93,
        explanation:
          "Путь — это последовательность вершин, в которой каждые две соседние вершины соединены ребром."
      }
    },
    {
      question: "Что называется деревом?",
      result: {
        status: "wrong",
        percent: 28,
        explanation:
          "Дерево — это связный граф без циклов."
      }
    }
  ];

  let currentIndex = 0;

  checkBtn.onclick = () => {
    const answer = answerInput.value.trim();
    if (!answer) return;

    const current = questions[currentIndex].result;

    resultBlock.classList.remove("hidden");
    percentBlock.textContent = `${current.percent}%`;
    explanationBlock.textContent = current.explanation;

    statusBlock.className = "result-status";

    if (current.status === "correct") {
      statusBlock.classList.add("result-status-correct");
      statusBlock.textContent = "Верно";
    } else if (current.status === "wrong") {
      statusBlock.classList.add("result-status-wrong");
      statusBlock.textContent = "Неверно";
    } else {
      statusBlock.classList.add("result-status-partial");
      statusBlock.textContent = "Частично верно";
    }
  };

  nextBtn.onclick = () => {
    currentIndex = (currentIndex + 1) % questions.length;

    questionBlock.textContent = questions[currentIndex].question;
    answerInput.value = "";
    resultBlock.classList.add("hidden");
  };
}