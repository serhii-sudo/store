const panel = document.getElementById("ai-panel");
const toggle = document.getElementById("ai-toggle");

const input = document.getElementById("chat-input");
const send = document.getElementById("send-btn");
const windowChat = document.getElementById("chat-window");


toggle.addEventListener("click", () => {
    panel.classList.toggle("open");
});


async function sendMessage() {

    const message = input.value.trim();

    if (!message)
        return;


    windowChat.innerHTML += `
        <div class="user-message">
            ${message}
        </div>
    `;

    input.value = "";

    windowChat.innerHTML += `
        <div id="thinking" class="ai-message">
            Думаю...
        </div>
    `;

    windowChat.scrollTop = windowChat.scrollHeight;


    const response = await fetch("/ai_gemini/chat/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });


    const data = await response.json();

    document.getElementById("thinking").remove();

    windowChat.innerHTML += `
        <div class="ai-message">
            ${data.answer}
        </div>
    `;

    windowChat.scrollTop = windowChat.scrollHeight;

}


send.addEventListener("click", sendMessage);

input.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});