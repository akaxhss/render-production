# Generated by Django 3.2.4 on 2021-07-07 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0032_auto_20210707_0946'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ConsultantDetails',
            new_name='SalesTeamDetails',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='consultant',
            new_name='sales',
        ),
    ]
