
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

function getTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function addMessage(message, sender, isHTML = false) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${sender}-message`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "bot" ? "✦" : "👤";

    const content = document.createElement("div");
    content.className = "message-content";

    const heading = document.createElement("strong");
    heading.textContent = sender === "bot"
        ? "CMS Events Assistant"
        : "You";

    const paragraph = document.createElement("p");

    if (isHTML) {
        paragraph.innerHTML = message;
    } else {
        paragraph.textContent = message;
    }

    const time = document.createElement("span");
    time.className = "message-time";
    time.textContent = getTime();

    content.appendChild(heading);
    content.appendChild(paragraph);
    content.appendChild(time);

    if (sender === "bot") {
        wrapper.appendChild(avatar);
        wrapper.appendChild(content);
    } else {
        wrapper.appendChild(content);
        wrapper.appendChild(avatar);
    }

    chatMessages.appendChild(wrapper);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(message) {
    message = message.trim();

    if (!message) return;

    addMessage(message, "user");

    userInput.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "...";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error("Server error");
        }

        addMessage(data.reply, "bot", true);

    } catch (error) {
        addMessage(
            "Unable to connect to the chatbot. Please check that the Flask server is running.",
            "bot"
        );
    }

    sendButton.disabled = false;
    sendButton.textContent = "SEND ➤";
    userInput.focus();
}

chatForm.addEventListener("submit", function(event) {
    event.preventDefault();
    sendMessage(userInput.value);
});

function sendSuggestion(message) {
    sendMessage(message);
}

function clearChat() {
    chatMessages.innerHTML = "";

    addMessage(
        "Hello! I am the CMS Event Manager Chatbot. How can I help you today?",
        "bot"
    );
}
