# Generated by Django 4.2.2 on 2023-12-24 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_remove_user_authenticat_deleted_7262c1_idx_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='user',
            name='authenticat_id_9bf31e_idx',
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['deleted_at', 'id'], name='authenticat_deleted_d736dc_idx'),
        ),
    ]