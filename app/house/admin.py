from django.contrib import admin
from .models import Configuration, UserProfileSearch

# Register your models here.

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(UserProfileSearch)
class UserProfileSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'term', 'created_at', 'get_tags_count')
    list_filter = ('created_at', 'user')
    search_fields = ('term', 'user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_tags_count(self, obj):
        return len(obj.tags) if obj.tags else 0
    get_tags_count.short_description = 'Qtd. Tags'

