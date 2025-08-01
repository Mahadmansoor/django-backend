# Generated by Django 5.2.3 on 2025-07-21 06:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0007_fileaccess_can_download_folderaccess_can_download'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_create_folder', models.BooleanField(default=False)),
                ('can_upload_folder', models.BooleanField(default=False)),
                ('can_upload_file', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
