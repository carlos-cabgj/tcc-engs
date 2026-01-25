from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tag Name")
    countUses = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 
    deleted_at = models.DateTimeField(null=True, blank=True) 
    lastUsed_at = models.DateTimeField(null=True, blank=True)
    create_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags',
        null=True,
        blank=True,
        verbose_name='Criada por'
    ) 

    # class Meta:
    #     verbose_name = "Produto"
    #     verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name