# Generated by Django 3.2.4 on 2023-08-11 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messages', '0002_alter_messages_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
