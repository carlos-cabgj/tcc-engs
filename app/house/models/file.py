from django.db import models
from django.contrib.auth.models import User
import os


def user_directory_path(instance, filename):
    """
    Retorna o caminho onde o arquivo será salvo.
    Formato: uploads/<username>/<filename>
    """
    # Obter username do usuário
    username = instance.user.username if instance.user else 'anonymous'
    # Retornar caminho: uploads/username/filename
    return os.path.join('uploads', username, filename)


def user_thumbnail_path(instance, filename):
    """
    Retorna o caminho onde o thumbnail será salvo.
    Formato: thumbnails/<username>/<filename>
    """
    # Obter username do usuário
    username = instance.user.username if instance.user else 'anonymous'
    # Retornar caminho: thumbnails/username/filename
    return os.path.join('thumbnails', username, filename)


class File(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Público'),
        ('users', 'Usuários'),
        ('private', 'Privado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="File Name")
    path = models.TextField(verbose_name="File Path", null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True, verbose_name="Arquivo")
    thumbnail = models.ImageField(upload_to=user_thumbnail_path, null=True, blank=True, verbose_name="Thumbnail")
    signature = models.CharField(max_length=64, verbose_name="File signature")
    extension = models.CharField(max_length=10, null=True, blank=True, verbose_name="Extensão do Arquivo")

    size = models.PositiveIntegerField(
        default=0,
        #validators=[MinValueValidator(0), MaxValueValidator(130)],
        null=False,
        blank=False,
    )
    views_count = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
    )
    
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='users',
        verbose_name="Visibilidade do Arquivo"
    )

    deleted_at = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True,
        verbose_name='Usuário que criou o arquivo'
    )

    #tags = models.ManyToManyField('Tag', related_name='File', blank=True)
    tags = models.ManyToManyField('Tag', through='FileTag', related_name='File')

    # class Meta:
    #     verbose_name = "Produto"
    #     verbose_name_plural = "Produtos"

    def save(self, *args, **kwargs):
        """Override save para capturar a extensão do arquivo automaticamente"""
        if self.file and not self.extension:
            # Extrair extensão do arquivo
            file_name = self.file.name
            _, ext = os.path.splitext(file_name)
            # Remover o ponto e converter para minúscula
            self.extension = ext.lstrip('.').lower() if ext else ''
        
        # Se não tem file mas tem name, tentar extrair do name
        if not self.extension and self.name:
            _, ext = os.path.splitext(self.name)
            self.extension = ext.lstrip('.').lower() if ext else ''
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name