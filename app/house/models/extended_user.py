from django.contrib.auth.models import User as DjangoUser
from django.db import models


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
        upload_to='profile_photos/%Y/%m/%d/',
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
