# Generated by Django 3.2.4 on 2021-07-02 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0024_user_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
        migrations.AddField(
            model_name='user',
            name='is_activee',
            field=models.BooleanField(default=True),
        ),
    ]
