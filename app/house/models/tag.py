from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tag Name")
    countUses = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField() 
    deleted_at = models.DateTimeField() 
    lastUsed_at = models.DateTimeField() 

    # class Meta:
    #     verbose_name = "Produto"
    #     verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name