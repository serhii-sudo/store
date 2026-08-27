// Инициализация

const panel = document.getElementById("ai-panel");
const username = panel.dataset.username;

let conversationId = localStorage.getItem("gemini_conversation_id");

const toggle = document.getElementById("ai-toggle");
const input = document.getElementById("chat-input");
const send = document.getElementById("send-btn");
const windowChat = document.getElementById("chat-window");


// UI открытие панели Gemini

function togglePanel() {
    panel.classList.toggle("open");
}


// Работа с сообщениями:
// Вопросы от пользователя

function renderUserMessage(message) {
    windowChat.innerHTML += `
        <div class="user-message">

            <div class="message-author">
                ${username}:
            </div>

            <div class="message-content">
                ${message}
            </div>

        </div>
    `;
}


// Ответы Gemini

function renderGeminiMessage(message) {
    windowChat.innerHTML += `
        <div class="ai-message">

            <div class="message-author">
                GEMINI:
            </div>

            <div class="message-content">
                ${message}
            </div>

        </div>
    `;
}

// линия-разделить между диалогами

function renderDivider() {
    windowChat.innerHTML += `
        <hr class="message-divider">
    `;
}


//  прокрутка сообщений

function scrollChatToBottom() {
    windowChat.scrollTop =
        windowChat.scrollHeight;
}


// Загрузка истории

async function loadChatHistory() {

    if (!conversationId) {
        return;
    }

    const response = await fetch(
        `/ai_gemini/chat/${conversationId}/`
    );

    const data = await response.json();

    if (!response.ok) {
        console.error(data);
        return;
    }

    windowChat.innerHTML = "";

    for (
        let i = 0;
        i < data.messages.length;
        i += 2
    ) {

        const userMessage = data.messages[i];
        const geminiMessage = data.messages[i + 1];

        renderUserMessage(
            userMessage.content
        );

        if (geminiMessage) {
            renderGeminiMessage(
                geminiMessage.content
            );
        }

        if (i + 2 < data.messages.length) {
            renderDivider();
        }
    }

    scrollChatToBottom();
}


// Отправка сообщения

async function sendMessage() {

    const message = input.value.trim();

    if (!message) {
        return;
    }

    renderUserMessage(message);

    input.value = "";

    const thinkingMessage =
        createThinkingMessage();

    windowChat.appendChild(
        thinkingMessage
    );

    scrollChatToBottom();

    const url = getChatUrl();

    try {

        const response = await fetch(
            url,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            console.error(data);

            thinkingMessage.remove();

            return;
        }

        saveConversationId(
            data.conversation_id
        );

        thinkingMessage.remove();

        renderGeminiMessage(
            data.answer
        );

        renderDivider();

        scrollChatToBottom();

    } catch (error) {

        console.error(
            "Ошибка запроса:",
            error
        );

        thinkingMessage.remove();
    }
}


// Вспомогательные функции:

function getChatUrl() {

    if (conversationId) {

        return `/ai_gemini/chat/${conversationId}/`;

    }

    return "/ai_gemini/chat/";
}


function saveConversationId(id) {

    conversationId = id;

    localStorage.setItem(
        "gemini_conversation_id",
        id
    );
}


function createThinkingMessage() {

    const element =
        document.createElement("div");

    element.className = "ai-message";

    element.innerHTML = `
        <div class="message-author">
            GEMINI
        </div>

        <div class="message-content">
            Думаю...
        </div>
    `;

    return element;
}


// События:

toggle.addEventListener(
    "click",
    togglePanel
);

send.addEventListener(
    "click",
    sendMessage
);

input.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {
            sendMessage();
        }

    }
);


// Start

loadChatHistory();