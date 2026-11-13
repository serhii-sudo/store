function googleLogin() {
    const rememberMe = document.getElementById('remember_me').checked;

    const form = document.createElement('form');
    form.method = 'POST';
    const googleUrl = document.getElementById('google-login').dataset.url;
    form.action = googleUrl;

    const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

    form.innerHTML = `
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}">
            <input type="hidden" name="remember_me" value="${rememberMe ? 'on' : ''}">
        `;

    document.body.appendChild(form);
    form.submit();
}

function telegramLogin() {
    const rememberMe = document.getElementById('remember_me').checked;

    const telegramButton = document.getElementById('telegram-login');
    const url = telegramButton.dataset.url;

    window.location.href = `${url}?remember_me=${rememberMe}`;
}

// from django.contrib.sessions.models import Session
// from django.utils import timezone
//
// for session in Session.objects.all():
//     data = session.get_decoded()
//     if data.get('_auth_user_id') == '71':
//         print('Дата истечения:', session.expire_date)
//         print('Осталось секунд:', (session.expire_date - timezone.now()).total_seconds())