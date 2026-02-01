
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profileForm');
    const profilePhotoInput = document.getElementById('profilePhoto');
    const photoPreview = document.getElementById('photoPreview');
    const photoFilename = document.getElementById('photoFilename');
    const statusMessage = document.getElementById('statusMessage');
    const errorMessage = document.getElementById('errorMessage');
    const submitBtn = form.querySelector('button[type="submit"]');

    // Obter token CSRF
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

    // Obter token JWT do localStorage
    function getJWTToken() {
        return localStorage.getItem('access_token');
    }

    // Obter dados do perfil
    async function loadProfileData() {
        try {
            const token = getJWTToken();
            const response = await fetch('/api/profile/me/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao carregar dados do perfil');
            }

            const data = await response.json();
            populateForm(data);
        } catch (error) {
            console.error('Erro:', error);
            showError('Erro ao carregar dados do perfil. Por favor, recarregue a página.');
        }
    }

    // Preencher formulário com dados do perfil
    function populateForm(data) {
        document.getElementById('firstName').value = data.first_name || '';
        document.getElementById('lastName').value = data.last_name || '';
        document.getElementById('username').value = data.username || '';
        document.getElementById('email').value = data.email || '';

        // Carregar foto se existir
        if (data.profile_photo) {
            photoPreview.src = data.profile_photo;
        }
    }

    // Preview de foto ao selecionar arquivo
    profilePhotoInput.addEventListener('change', function(e) {
        const file = this.files[0];
        
        if (file) {
            // Validar tipo de arquivo
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                showError('Por favor, selecione uma imagem válida (JPEG, PNG, GIF ou WebP)');
                this.value = '';
                return;
            }

            // Validar tamanho (máximo 5MB)
            const maxSize = 5 * 1024 * 1024; // 5MB
            if (file.size > maxSize) {
                showError('A imagem não pode ter mais de 5MB');
                this.value = '';
                return;
            }

            // Mostrar preview
            const reader = new FileReader();
            reader.onload = function(event) {
                photoPreview.src = event.target.result;
                photoFilename.textContent = file.name;
            };
            reader.readAsDataURL(file);
        }
    });

    // Clique na câmera abre o seletor de arquivo
    document.querySelector('.photo-upload-label').addEventListener('click', function(e) {
        e.preventDefault();
        profilePhotoInput.click();
    });

    // Enviar formulário
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validar senhas se estiverem preenchidas
        const currentPasswordField = document.getElementById('currentPassword');
        const newPasswordField = document.getElementById('newPassword');
        const confirmPasswordField = document.getElementById('confirmPassword');
        
        const currentPassword = currentPasswordField ? currentPasswordField.value : '';
        const newPassword = newPasswordField ? newPasswordField.value : '';
        const confirmPassword = confirmPasswordField ? confirmPasswordField.value : '';

        if (newPassword || confirmPassword || currentPassword) {
            if (!currentPassword) {
                showError('Digite sua senha atual para alterá-la');
                return;
            }
            if (!newPassword) {
                showError('Digite a nova senha');
                return;
            }
            if (newPassword.length < 6) {
                showError('A nova senha deve ter no mínimo 6 caracteres');
                return;
            }
            if (newPassword !== confirmPassword) {
                showError('As senhas não coincidem');
                return;
            }
        }

        // Desabilitar botão
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');

        try {
            const token = getJWTToken();
            const formData = new FormData();

            // Adicionar dados do formulário
            formData.append('first_name', document.getElementById('firstName').value);
            formData.append('last_name', document.getElementById('lastName').value);
            formData.append('email', document.getElementById('email').value);

            // Adicionar senhas se preenchidas
            if (currentPassword && newPassword) {
                formData.append('current_password', currentPassword);
                formData.append('new_password', newPassword);
            }

            // Adicionar foto se selecionada
            if (profilePhotoInput.files.length > 0) {
                formData.append('profile_photo', profilePhotoInput.files[0]);
            }

            const response = await fetch('/api/profile/me/', {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData
            });

            const responseData = await response.json();
            
            if (!response.ok) {
                console.error('Erro na resposta:', responseData);
                const errorMsg = responseData.error || responseData.message || responseData.detail || 'Erro ao atualizar perfil';
                throw new Error(errorMsg);
            }

            showSuccess(responseData.message || 'Perfil atualizado com sucesso!');
            
            // Limpar campos de senha se existirem
            if (currentPasswordField) currentPasswordField.value = '';
            if (newPasswordField) newPasswordField.value = '';
            if (confirmPasswordField) confirmPasswordField.value = '';
            
            // Recarregar dados após sucesso
            setTimeout(() => {
                loadProfileData();
            }, 1000);

        } catch (error) {
            console.error('Erro:', error);
            showError(error.message || 'Erro ao atualizar perfil. Verifique os dados e tente novamente.');
        } finally {
            // Reabilitar botão
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    });

    // Mostrar mensagem de sucesso
    function showSuccess(message) {
        statusMessage.textContent = message;
        statusMessage.style.display = 'block';
        errorMessage.style.display = 'none';

        // Esconder mensagem após 5 segundos
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 5000);
    }

    // Mostrar mensagem de erro
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        statusMessage.style.display = 'none';

        // Esconder mensagem após 5 segundos
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // Carregar dados do perfil ao abrir a página
    loadProfileData();
});
