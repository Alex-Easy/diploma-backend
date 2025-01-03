# Generated by Django 5.1.4 on 2024-12-23 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_alter_emailconfirmation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailconfirmation',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='email_confirmation', to='backend.user'),
        ),
    ]
