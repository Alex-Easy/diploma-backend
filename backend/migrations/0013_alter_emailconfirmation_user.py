# Generated by Django 5.1.4 on 2024-12-23 20:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_alter_emailconfirmation_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailconfirmation',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='email_confirmation', to=settings.AUTH_USER_MODEL),
        ),
    ]
