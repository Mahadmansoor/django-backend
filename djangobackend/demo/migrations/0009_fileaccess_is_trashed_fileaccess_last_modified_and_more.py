# Generated by Django 5.2.3 on 2025-07-21 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0008_userpermissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileaccess',
            name='is_trashed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fileaccess',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='fileaccess',
            name='trashed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='folderaccess',
            name='is_trashed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='folderaccess',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='folderaccess',
            name='trashed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
