# Generated by Django 4.2.2 on 2023-12-25 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_alter_loancustomer_monthly_income_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bankpersonnel',
            options={'managed': True, 'permissions': [('can_approve_applicant', 'Can approve applicant'), ('can_reject_applicant', 'Can reject applicant')]},
        ),
    ]
