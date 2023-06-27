const chatContainer = document.getElementById("chat-container");
const usernameInput = document.getElementById("username-input");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

const socket = new WebSocket(`ws://${window.location.host}/ws`);

socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    const messageElement = document.createElement("p");
    messageElement.textContent = `${message.username}: ${message.message}`;
    chatContainer.appendChild(messageElement);
};

sendButton.addEventListener("click", () => {
    const username = usernameInput.value.trim();
    const message = messageInput.value.trim();
    if (username && message) {
        const data = `${username}:${message}`;
        socket.send(data);
        messageInput.value = "";
    }
});

