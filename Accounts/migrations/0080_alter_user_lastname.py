# Generated by Django 3.2.4 on 2021-11-01 05:08

import Accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0079_alter_user_lastname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='lastname',
            field=models.CharField(default='lname', max_length=100, validators=[Accounts.validators.CheckIfAlpha]),
            preserve_default=False,
        ),
    ]
