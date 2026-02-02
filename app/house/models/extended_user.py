from django.contrib.auth.models import User as DjangoUser
from django.db import models
import os
import uuid


def user_profile_photo_path(instance, filename):
    """
    Retorna o caminho onde a foto de perfil será salva.
    Formato: profile_photos/<username>/<uuid>.<extensão>
    """
    # Obter username do usuário
    username = instance.user.username if instance.user else 'anonymous'
    # Gerar UUID para o arquivo
    file_uuid = uuid.uuid4()
    # Extrair extensão do arquivo original
    ext = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
    # Retornar caminho: profile_photos/username/uuid.ext
    return os.path.join('profile_photos', username, f"{file_uuid}.{ext}")


class UserProfile(models.Model):
    """Extensão do User padrão com campos adicionais"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('user', 'Usuário'),
        ('visitor', 'Visitante'),
    ]
    
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    profile_img = models.ImageField(
        upload_to=user_profile_photo_path,
        null=True,
        blank=True,
        verbose_name='Foto de Perfil'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Função'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"


# Alias para compatibilidade
User = DjangoUser
