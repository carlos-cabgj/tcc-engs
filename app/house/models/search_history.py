from django.contrib.auth.models import User as DjangoUser
from django.db import models


class UserProfileSearch(models.Model):
    """Histórico de buscas do usuário"""
    
    user = models.ForeignKey(
        DjangoUser,
        on_delete=models.CASCADE,
        related_name='search_history',
        verbose_name='Usuário'
    )
    term = models.CharField(
        max_length=255,
        verbose_name='Termo Pesquisado'
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tags Utilizadas',
        help_text='Lista de tags aplicadas na busca'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    class Meta:
        verbose_name = 'Histórico de Busca'
        verbose_name_plural = 'Históricos de Busca'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['term']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.term} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
