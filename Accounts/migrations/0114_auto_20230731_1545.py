# Generated by Django 3.2.4 on 2023-07-31 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0113_user_fcm_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='fcm_token',
        ),
        migrations.AddField(
            model_name='user',
            name='fcm_tokenn',
            field=models.TextField(blank=True, null=True),
        ),
    ]
