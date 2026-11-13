// const interval = setInterval(async () => {
//     try {
//         const res = await fetch(
//             `/user/telegram/check/?code=${window.TG_CODE}`
//         );
//
//         const data = await res.json();
//
//         if (
//             data.status === "already_authenticated" ||
//             data.status === "ok" ||
//             data.status === "linked"
//         ) {
//             clearInterval(interval);
//             window.location.href = "/";
//         }
//
//         if (data.status === "expired" || data.status === "error") {
//             clearInterval(interval);
//             console.log("Telegram:", data.status);
//         }
//
//     } catch (error) {
//         console.error("Telegram polling error:", error);
//     }
//
// }, 2000);
//
// // Через 10 секунд прекращаем запросы
// setTimeout(() => {
//     clearInterval(interval);
//     console.log("Время ожидания истекло");
// }, 60000);
//
// console.log("TG CODE:", window.TG_CODE);
// console.log("Polling started");

// data.status === "ok" - если сервер авторизировал юзера раньше времени - то, останавливаем сервер
// clearInterval(interval) - остановить повторяющиеся запросы на сервер
// Polling — это когда клиент (обычно браузер или JS) сам постоянно спрашивает сервер, есть ли изменения

const POLLING_INTERVAL = 2000;
const POLLING_TIMEOUT = 60000;

let isChecking = false;

const interval = setInterval(async () => {
    if (isChecking) return;

    isChecking = true;

    try {
        const res = await fetch(
            `/user/telegram/check/?code=${encodeURIComponent(window.TG_CODE)}`
        );

        if (!res.ok) {
            throw new Error(`HTTP error: ${res.status}`);
        }

        const data = await res.json();

        switch (data.status) {
            case "pending":
                // Ожидаем подтверждения от Telegram
                break;

            case "ok":
            case "linked":
                // Авторизация или привязка успешна
                clearInterval(interval);
                window.location.href = "/";
                break;

            case "already_authenticated":
                clearInterval(interval);
                window.location.href = "/";
                break;

            case "expired":
                clearInterval(interval);
                console.log("Код устарел");
                break;

            case "already_used":
                clearInterval(interval);
                console.log("Код уже использован");
                break;

            case "error":
            case "unknown_purpose":
                clearInterval(interval);
                console.log("Ошибка Telegram:", data.status);
                break;

            default:
                clearInterval(interval);
                console.log("Неизвестный статус:", data.status);
        }

    } catch (error) {
        console.error("Telegram polling error:", error);

    } finally {
        isChecking = false;
    }

}, POLLING_INTERVAL);

setTimeout(() => {
    clearInterval(interval);
    console.log("Время ожидания истекло");
}, POLLING_TIMEOUT);

console.log("Polling started");