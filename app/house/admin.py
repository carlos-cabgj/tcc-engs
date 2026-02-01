from django.contrib import admin
from .models import Configuration

# Register your models here.

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
