const API_URL = "https://agent-k45k.onrender.com/chat";

function addMessage(text, type) {
  const chat = document.getElementById("chat");

  const div = document.createElement("div");
  div.classList.add("msg", type);
  div.innerText = text;

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("input");
  const text = input.value;

  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  const res = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: text })
  });

  const data = await res.json();

  addMessage(data.reply, "bot");
}

document.getElementById("input").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});