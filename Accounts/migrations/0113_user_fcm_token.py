# Generated by Django 3.2.4 on 2023-07-31 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0112_remove_user_fcm_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcm_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]