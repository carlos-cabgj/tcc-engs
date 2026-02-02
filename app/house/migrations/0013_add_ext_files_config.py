# Generated migration

from django.db import migrations


def add_ext_files_configuration(apps, schema_editor):
    """Adiciona a configuração de extensões de arquivos"""
    Configuration = apps.get_model('house', 'Configuration')
    
    ext_files_config = {
        "text": ["txt"],
        "docs": ["doc", "docx", "pdf"],
        "spreadsheet": ["csv", "xls", "xlsx"],
        "audio": ["mp3", "wav"],
        "video": ["mp4", "avi", "mkv"],
        "folder": ["zip"],
        "image": ["png","jpg","jpeg","gif"]
    }
    
    # Criar ou atualizar a configuração
    Configuration.objects.update_or_create(
        name='ext_files',
        defaults={'config': ext_files_config}
    )


def reverse_ext_files_configuration(apps, schema_editor):
    """Remove a configuração de extensões de arquivos"""
    Configuration = apps.get_model('house', 'Configuration')
    Configuration.objects.filter(name='ext_files').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0012_configuration_file_extension'),
    ]

    operations = [
        migrations.RunPython(
            add_ext_files_configuration,
            reverse_ext_files_configuration
        ),
    ]
