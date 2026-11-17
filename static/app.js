const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("send-button");

function addMessage(text, kind) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${kind}`;
  bubble.textContent = text;
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
    if (!response.ok) throw new Error("Server response was not successful.");
    const data = await response.json();
    addMessage(data.reply || "I don't have an answer for that yet.", "bot");
  } catch (error) {
    addMessage("I couldn't connect to the chatbot. Check that the Flask server is running and try again.", "bot");
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
  button.addEventListener("click", () => ask(button.dataset.question));
});
