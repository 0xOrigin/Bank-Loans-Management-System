# Generated by Django 4.2.2 on 2023-12-21 20:14

import authentication.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=authentication.models.User.get_user_picture_upload_path)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'managed': True,
                'indexes': [models.Index(fields=['id'], name='authenticat_id_9bf31e_idx'), models.Index(fields=['username'], name='authenticat_usernam_61ef80_idx'), models.Index(fields=['email'], name='authenticat_email_d74434_idx'), models.Index(fields=['id', 'email', 'username'], name='authenticat_id_a793ac_idx')],
            },
        ),
    ]
