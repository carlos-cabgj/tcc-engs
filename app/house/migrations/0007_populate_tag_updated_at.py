from django.db import migrations
from django.utils import timezone


def populate_updated_at(apps, schema_editor):
    """Preencher updated_at com o valor de created_at ou data atual"""
    Tag = apps.get_model('house', 'Tag')
    for tag in Tag.objects.filter(updated_at__isnull=True):
        tag.updated_at = tag.created_at or timezone.now()
        tag.save(update_fields=['updated_at'])


def reverse_populate(apps, schema_editor):
    """Reverter para NULL"""
    Tag = apps.get_model('house', 'Tag')
    Tag.objects.all().update(updated_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0006_fix_tag_updated_at'),
    ]

    operations = [
        migrations.RunPython(populate_updated_at, reverse_populate),
    ]
