# Generated by Django 3.2.4 on 2021-07-26 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0048_alter_customerdetails_consultant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerdetails',
            name='consultant',
        ),
    ]
