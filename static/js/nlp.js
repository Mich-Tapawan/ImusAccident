document.addEventListener("DOMContentLoaded", () => {
  const sendButton = document.getElementById("search");
  const userInput = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-container");

  sendButton.addEventListener("click", () => {
    const userMessage = userInput.value;
    if (userMessage.trim()) {
      addMessageToChat(userMessage, "user");
      chatbot(userMessage);
      userInput.value = "";
    }
  });

  function addMessageToChat(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.classList.add(
      sender === "user" ? "user-message" : "bot-message"
    );
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
  }

  async function chatbot(chat) {
    console.log(chat);
    try {
      const res = await fetch("http://localhost:5000/handlePrompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: chat }),
      });
      const data = await res.json();
      console.log(data);

      addMessageToChat(data, "bot");
    } catch (error) {
      addMessageToChat("I'm sorry. I don't have any data for that.", "bot");
    }
  }
});
