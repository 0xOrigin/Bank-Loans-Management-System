# Generated by Django 4.2.2 on 2023-12-26 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0012_alter_loan_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loan',
            options={'managed': True, 'permissions': [('can_approve_loan', 'Can approve loan'), ('can_release_loan', 'Can release loan'), ('can_disburse_loan', 'Can disburse loan'), ('can_reject_loan', 'Can reject loan')]},
        ),
    ]
