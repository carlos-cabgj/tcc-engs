
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const submitBtn = loginForm.querySelector('button[type="submit"]');

    // Gerenciar envio do formulário
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Desabilitar botão
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        try {
            // Fazer login na API
            const response = await fetch('/api/token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao fazer login');
            }

            const data = await response.json();
            
            // Armazenar tokens
            const accessToken = data.access;
            const refreshToken = data.refresh;

            // Armazenar em cookies
            setCookie('access_token', accessToken, 1); // 1 dia
            setCookie('refresh_token', refreshToken, 7); // 7 dias
            
            // Também armazenar em localStorage para backup
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);

            showSuccess('Login realizado com sucesso! Redirecionando...');

            // Redirecionar após 1.5 segundos
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);

        } catch (error) {
            console.error('Erro:', error);
            showError(error.message || 'Erro ao fazer login. Verifique suas credenciais.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    });

    // Mostrar mensagem de erro
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    // Mostrar mensagem de sucesso
    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
    }

    // Alternar visibilidade da senha
    window.togglePassword = function() {
        const passwordInput = document.getElementById('password');
        const toggleBtn = document.querySelector('.toggle-password i');

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleBtn.classList.remove('fa-eye');
            toggleBtn.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            toggleBtn.classList.remove('fa-eye-slash');
            toggleBtn.classList.add('fa-eye');
        }
    };

    // Função para definir cookie
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        const expiresString = 'expires=' + expires.toUTCString();
        document.cookie = name + '=' + value + '; ' + expiresString + '; path=/; SameSite=Lax';
    }

    // Função para obter cookie
    window.getCookie = function(name) {
        const nameEQ = name + '=';
        const cookies = document.cookie.split(';');
        
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.indexOf(nameEQ) === 0) {
                return cookie.substring(nameEQ.length);
            }
        }
        
        return null;
    };

    // Verificar se já está logado
    const token = getCookie('access_token') || localStorage.getItem('access_token');
    if (token) {
        window.location.href = '/';
    }
});
