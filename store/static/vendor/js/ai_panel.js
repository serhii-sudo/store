// Инициализация

const panel = document.getElementById("ai-panel");
const username = panel.dataset.username;

let conversationId = localStorage.getItem("gemini_conversation_id");

const toggle = document.getElementById("ai-toggle");
const input = document.getElementById("chat-input");
const send = document.getElementById("send-btn");
const clear = document.getElementById("clear-btn");
const windowChat = document.getElementById("chat-window");

console.log("CLEAR BUTTON:", clear);


// UI: открытие панели Gemini

function togglePanel() {
    panel.classList.toggle("open");
}


// Создание сообщения

function createMessageElement(author, message, className) {
    const messageElement = document.createElement("div");
    messageElement.className = className;

    const authorElement = document.createElement("div");
    authorElement.className = "message-author";
    authorElement.textContent = author;

    const contentElement = document.createElement("div");
    contentElement.className = "message-content";

    // Безопасно отображаем текст и ссылки.
    renderMessageContent(contentElement, message);

    messageElement.appendChild(authorElement);
    messageElement.appendChild(contentElement);

    return messageElement;
}


// Безопасное отображение текста и ссылок

function renderMessageContent(container, message) {
    const text = String(message ?? "");

    // Распознаём абсолютные HTTP(S) URL и относительные URL товаров.
    const urlPattern =
        /https?:\/\/[^\s<>"']+|\/product_detail\/\d+\/?/g;

    let lastIndex = 0;
    let match;

    while ((match = urlPattern.exec(text)) !== null) {
        const rawUrl = match[0];

        // Добавляем обычный текст перед ссылкой.
        container.appendChild(
            document.createTextNode(
                text.slice(lastIndex, match.index)
            )
        );

        // Убираем конечную пунктуацию, если она попала в URL.
        const urlMatch = rawUrl.match(
            /[.,!?;:)\]}]+$/
        );

        const trailingPunctuation = urlMatch
            ? urlMatch[0]
            : "";

        const url = trailingPunctuation
            ? rawUrl.slice(0, -trailingPunctuation.length)
            : rawUrl;

        let parsedUrl;

        try {
            parsedUrl = new URL(url, window.location.origin);
        } catch {
            container.appendChild(
                document.createTextNode(rawUrl)
            );

            lastIndex = urlPattern.lastIndex;
            continue;
        }

        const isRelativeProductUrl =
            url.startsWith("/product_detail/");

        const isAllowedAbsoluteUrl =
            parsedUrl.protocol === "https:" ||
            parsedUrl.protocol === "http:";

        const isSameOrigin =
            parsedUrl.origin === window.location.origin;

        if (
            isRelativeProductUrl &&
            isSameOrigin
        ) {
            // Разрешаем только ссылки на страницы товаров.
            const link = document.createElement("a");

            link.href = parsedUrl.href;
            link.textContent = url;
            link.target = "_self";

            container.appendChild(link);

        } else if (
            !isRelativeProductUrl &&
            isAllowedAbsoluteUrl
        ) {
            // Для внешних ссылок используем новую вкладку.
            const link = document.createElement("a");

            link.href = parsedUrl.href;
            link.textContent = url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";

            container.appendChild(link);

        } else {
            container.appendChild(
                document.createTextNode(url)
            );
        }

        // Добавляем пунктуацию после ссылки.
        if (trailingPunctuation) {
            container.appendChild(
                document.createTextNode(trailingPunctuation)
            );
        }

        lastIndex = urlPattern.lastIndex;
    }

    // Добавляем оставшийся текст.
    container.appendChild(
        document.createTextNode(
            text.slice(lastIndex)
        )
    );
}


// Сообщение пользователя

function renderUserMessage(message) {
    const element = createMessageElement(
        username,
        message,
        "user-message"
    );

    windowChat.appendChild(element);
}


// Ответ Gemini

function renderGeminiMessage(message) {
    const element = createMessageElement(
        "GEMINI:",
        message,
        "ai-message"
    );

    windowChat.appendChild(element);
}


// Разделитель между диалогами

function renderDivider() {
    const divider = document.createElement("hr");

    divider.className = "message-divider";

    windowChat.appendChild(divider);
}


// Прокрутка сообщений

function scrollChatToBottom() {
    windowChat.scrollTop = windowChat.scrollHeight;
}


// Загрузка истории

async function loadChatHistory() {
    if (!conversationId) {
        return;
    }

    try {
        const response = await fetch(
            `/ai_gemini/chat/${conversationId}/`
        );

        const data = await response.json();

        if (!response.ok) {
            console.error(data);
            return;
        }

        windowChat.replaceChildren();

        for (let i = 0; i < data.messages.length; i += 2) {
            const userMessage = data.messages[i];
            const geminiMessage = data.messages[i + 1];

            if (userMessage) {
                renderUserMessage(userMessage.content);
            }

            if (geminiMessage) {
                renderGeminiMessage(geminiMessage.content);
            }

            if (i + 2 < data.messages.length) {
                renderDivider();
            }
        }

        scrollChatToBottom();

    } catch (error) {
        console.error("Ошибка загрузки истории:", error);
    }
}


// Отправка сообщения

async function sendMessage() {
    const message = input.value.trim();

    if (!message) {
        return;
    }

    renderUserMessage(message);

    input.value = "";

    const thinkingMessage = createThinkingMessage();

    windowChat.appendChild(thinkingMessage);

    scrollChatToBottom();

    const url = getChatUrl();

    send.disabled = true;

    try {
        const response = await fetch(url, {
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
            console.error(data);

            thinkingMessage.remove();

            renderGeminiMessage(
                data.error || "Не удалось получить ответ."
            );

            return;
        }

        saveConversationId(data.conversation_id);

        thinkingMessage.remove();

        renderGeminiMessage(data.answer);

if (data.products && data.products.length > 0) {
    const productsContainer = document.createElement("div");
    productsContainer.className = "message-content";

    const title = document.createElement("p");
    title.textContent = "Найденные товары:";
    productsContainer.appendChild(title);

    data.products.forEach(product => {
        const link = document.createElement("a");
        link.href = product.url;
        link.textContent = product.name;
        link.className = "product-link";
        productsContainer.appendChild(link);
        productsContainer.appendChild(document.createElement("br"));
    });

    windowChat.appendChild(productsContainer);
}

        renderDivider();

        scrollChatToBottom();

    } catch (error) {
        console.error("Ошибка запроса:", error);

        thinkingMessage.remove();

        renderGeminiMessage(
            "Не удалось связаться с сервером. Попробуйте ещё раз."
        );

    } finally {
        send.disabled = false;
    }
}


// Вспомогательные функции

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
    const element = document.createElement("div");

    element.className = "ai-message";

    const author = document.createElement("div");
    author.className = "message-author";
    author.textContent = "GEMINI:";

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = "Думаю...";

    element.appendChild(author);
    element.appendChild(content);

    return element;
}


// Удаление истории чата

async function clearChat() {
    console.log("CLEAR CHAT");
    console.log("conversationId:", conversationId);

    if (!conversationId) {
        console.log("conversationId отсутствует");
        return;
    }

    try {
        const response = await fetch(
            `/ai_gemini/chat/${conversationId}/`,
            {
                method: "DELETE"
            }
        );

        console.log("DELETE STATUS:", response.status);

        const data = await response.json();

        console.log("DELETE RESPONSE:", data);

        if (!response.ok) {
            console.error("Ошибка очистки чата:", data);
            return;
        }

        windowChat.replaceChildren();

        localStorage.removeItem("gemini_conversation_id");

        conversationId = null;

    } catch (error) {
        console.error("Ошибка запроса:", error);
    }
}


// События

toggle.addEventListener("click", togglePanel);

send.addEventListener("click", sendMessage);

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

clear.addEventListener("click", clearChat);


// Запуск

loadChatHistory();