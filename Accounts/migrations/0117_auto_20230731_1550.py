# Generated by Django 3.2.4 on 2023-07-31 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0116_alter_firebasefcm_fcm_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerdetails',
            name='fcm_token',
        ),
        migrations.RemoveField(
            model_name='user',
            name='fcm_token',
        ),
        migrations.AlterField(
            model_name='firebasefcm',
            name='fcm_token',
            field=models.TextField(unique=True),
        ),
    ]
