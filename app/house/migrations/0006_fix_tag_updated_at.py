from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0005_remove_not_null_deleted_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
