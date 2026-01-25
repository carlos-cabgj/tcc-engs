from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Público'),
        ('users', 'Usuários'),
        ('private', 'Privado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="File Name")
    path = models.TextField(verbose_name="File Path", null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True, verbose_name="Arquivo")
    signature = models.CharField(max_length=64, verbose_name="File signature")

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

    def __str__(self):
        return self.name