const interval = setInterval(async () => {
    const res = await fetch(`/user/telegram/check/?code=${window.TG_CODE}`);
    const data = await res.json();

    if (data.status === "ok") {
        clearInterval(interval);
        window.location.href = "/";
    }
}, 1000); // Polling

console.log("TG CODE:", window.TG_CODE);
console.log("tick", Date.now());


// data.status === "ok" - если сервер авторизировал юзера раньше времени - то, останавливаем сервер
// clearInterval(interval) - остановить повторяющиеся запросы на сервер
// Polling — это когда клиент (обычно браузер или JS) сам постоянно спрашивает сервер, есть ли изменения