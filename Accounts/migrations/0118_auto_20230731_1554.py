# Generated by Django 3.2.4 on 2023-07-31 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0117_auto_20230731_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerdetails',
            name='fcm_token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='fcm_token',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]