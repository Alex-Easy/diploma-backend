# Generated by Django 5.1.4 on 2024-12-22 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_remove_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, default='', max_length=255, unique=True),
        ),
    ]
