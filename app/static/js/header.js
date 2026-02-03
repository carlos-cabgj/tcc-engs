function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax';
}

function logout() {
    // Limpar cookies
    deleteCookie('access_token');
    deleteCookie('refresh_token');

    // Limpar localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Redirecionar para login
    window.location.href = '/login';
}

// Validar autenticação e carregar dados do perfil
document.addEventListener('DOMContentLoaded', async function() {
    const userIconsDiv = document.getElementById('userIcons');
    const accessToken = getCookie('access_token') || localStorage.getItem('access_token');

    if (!accessToken) {
        // Usuário não está logado
        userIconsDiv.innerHTML = `
            <a id="loginLink" href="/login" style="color: white; text-decoration: none; font-size: 1.1em; display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-sign-in-alt"></i> Login
            </a>
        `;
        // Adicionar evento ao link de login
        document.getElementById('loginLink').addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/login';
        });
        return;
    }

    // Usuário está logado, carregar dados do perfil
    try {
        const response = await fetch('/api/profile/me/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            const profilePhoto = data.profile_photo;
            const userName = data.first_name || data.username || 'Usuário';

            // Montar a URL da imagem do perfil
            let photoUrl = '/static/img/default-avatar.svg'; // imagem padrão
            if (profilePhoto) {
                // Se é URL completa
                if (profilePhoto.startsWith('http')) {
                    photoUrl = profilePhoto;
                } else {
                    // Se é caminho relativo
                    photoUrl = profilePhoto.startsWith('/') ? profilePhoto : `/media/${profilePhoto}`;
                }
            }

            // Montar HTML do usuário logado
            userIconsDiv.innerHTML = `
                <div class="user-menu" style="display: flex; flex-direction: column; align-items: center; gap: 5px;">
                    <span style="color: white; font-size: 0.95em;">${userName}</span>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <a href="/profile" title="Editar Perfil" style="color: white; text-decoration: none; margin: 0;">
                            <img src="${photoUrl}" alt="Perfil" style="width: 4em; height: 4em; border-radius: 50%; object-fit: cover; border: 2px solid white;">
                        </a>
                        <button id="logoutBtn" title="Sair" style="background: none; border: none; color: white; font-size: 1em; cursor: pointer; margin: 0;">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                    </div>
                </div>
            `;

            // Adicionar evento ao botão de logout
            document.getElementById('logoutBtn').addEventListener('click', logout);
        } else if (response.status === 401) {
            // Token expirado ou inválido
            deleteCookie('access_token');
            deleteCookie('refresh_token');
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.reload();
        } else {
            // Erro ao carregar perfil
            userIconsDiv.innerHTML = `
                <a href="/login" style="color: white; text-decoration: none; font-size: 1.1em; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-sign-in-alt"></i> Login
                </a>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        userIconsDiv.innerHTML = `
            <a href="/login" style="color: white; text-decoration: none; font-size: 1.1em; display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-sign-in-alt"></i> Login
            </a>
        `;
    }
});
