# Generated by Django 4.2.2 on 2023-12-24 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_remove_loancustomer_loans_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='user',
            name='authenticat_deleted_7262c1_idx',
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['deleted_at', 'username'], name='authenticat_deleted_6dfccb_idx'),
        ),
    ]