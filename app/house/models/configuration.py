from django.db import models


class Configuration(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Configuration Name")
    config = models.JSONField(verbose_name="Configuration Data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"

    def __str__(self):
        return self.name
