const API_URL = "https://agent-k45k.onrender.com/chat";

let chatHistory = JSON.parse(localStorage.getItem("chat")) || [];

document.getElementById("input").addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

function addMessage(text, type, save = true) {
  const chat = document.getElementById("chat");

  const div = document.createElement("div");
  div.classList.add("msg", type);
  div.innerText = text;

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;

  if (save) {
    chatHistory.push({ text, type });
    localStorage.setItem("chat", JSON.stringify(chatHistory));
  }
}

function showTyping() {
  const chat = document.getElementById("chat");

  const typing = document.createElement("div");
  typing.classList.add("msg", "bot");
  typing.id = "typing";
  typing.innerText = "Escribiendo...";

  chat.appendChild(typing);
  chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}

async function sendMessage() {
  const input = document.getElementById("input");
  const text = input.value.trim();

  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  showTyping();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();

    removeTyping();

    if (data.reply) {
      addMessage(data.reply, "bot");
    } else {
      addMessage("Error: respuesta inválida", "bot");
    }

  } catch (error) {
    removeTyping();
    addMessage("Error conectando con el servidor", "bot");
  }
}

window.onload = () => {
  const chat = document.getElementById("chat");

  // 🔥 FIX CLAVE: limpiar SIEMPRE antes de renderizar
  chat.innerHTML = "";

  chatHistory.forEach(msg => {
    const div = document.createElement("div");
    div.classList.add("msg", msg.type);
    div.innerText = msg.text;
    chat.appendChild(div);
  });

  chat.scrollTop = chat.scrollHeight;
};

async function clearChat() {
  try {
    await fetch("https://agent-k45k.onrender.com/clear", {
      method: "POST"
    });
  } catch (e) {}

  chatHistory = [];
  localStorage.removeItem("chat");

  document.getElementById("chat").innerHTML = "";
}