
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("send-button");

// Safely format chatbot responses
function formatMessage(text) {
  const lines = String(text).split("\n");
  const container = document.createElement("div");

  let table = null;
  let tbody = null;
  let list = null;

  function flushList() {
    if (list) {
      container.appendChild(list);
      list = null;
    }
  }

  function flushTable() {
    if (table) {
      container.appendChild(table);
      table = null;
      tbody = null;
    }
  }

  function addInlineText(parent, value) {
    // Escape HTML by using text nodes, then format **bold**
    const parts = value.split(/(\*\*.*?\*\*)/g);

    parts.forEach(part => {
      if (part.startsWith("**") && part.endsWith("**")) {
        const strong = document.createElement("strong");
        strong.textContent = part.slice(2, -2);
        parent.appendChild(strong);
      } else {
        parent.appendChild(document.createTextNode(part));
      }
    });
  }

  lines.forEach(line => {
    const trimmed = line.trim();

    // Markdown table rows
    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      flushList();

      const cells = trimmed
        .slice(1, -1)
        .split("|")
        .map(cell => cell.trim());

      // Skip Markdown separator rows
      if (cells.every(cell => /^:?-{3,}:?$/.test(cell))) {
        return;
      }

      if (!table) {
        table = document.createElement("table");
        table.className = "chat-table";

        const thead = document.createElement("thead");
        const row = document.createElement("tr");

        cells.forEach(cell => {
          const th = document.createElement("th");
          addInlineText(th, cell);
          row.appendChild(th);
        });

        thead.appendChild(row);
        table.appendChild(thead);

        tbody = document.createElement("tbody");
        table.appendChild(tbody);
      } else {
        const row = document.createElement("tr");

        cells.forEach(cell => {
          const td = document.createElement("td");
          addInlineText(td, cell);
          row.appendChild(td);
        });

        tbody.appendChild(row);
      }

      return;
    }

    flushTable();

    if (!trimmed) {
      flushList();
      return;
    }

    // Bullet lists
    if (/^[-*]\s+/.test(trimmed)) {
      if (!list) list = document.createElement("ul");

      const li = document.createElement("li");
      addInlineText(li, trimmed.replace(/^[-*]\s+/, ""));
      list.appendChild(li);
      return;
    }

    flushList();

    const paragraph = document.createElement("p");
    addInlineText(paragraph, trimmed);
    container.appendChild(paragraph);
  });

  flushList();
  flushTable();

  return container;
}

function addMessage(text, kind) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${kind}`;
  bubble.appendChild(formatMessage(text));

  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
}

async function ask(question) {
  const clean = question.trim();
  if (!clean) return;

  addMessage(clean, "user");
  input.value = "";
  sendButton.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: clean })
    });

    if (!response.ok) {
      throw new Error("Server response was not successful.");
    }

    const data = await response.json();

    addMessage(
      data.reply || "I don't have an answer for that yet.",
      "bot"
    );
  } catch (error) {
    addMessage(
      "I couldn't connect to the chatbot. Check that the Flask server is running and try again.",
      "bot"
    );
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  ask(input.value);
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    ask(button.dataset.question);
  });
});
