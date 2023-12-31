# Generated by Django 3.2.4 on 2021-09-03 09:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0067_auto_20210828_0909'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerdetails',
            name='consultant',
        ),
        migrations.AlterField(
            model_name='customerdetails',
            name='abortions',
            field=models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Enter either yes/no', regex='^(?i:yes|yess|yyess|no|noo|nnoo)$')]),
        ),
        migrations.AlterField(
            model_name='customerdetails',
            name='babies_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customerdetails',
            name='diabetes',
            field=models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Enter either yes/no', regex='^(?i:yes|yess|yyess|no|noo|nnoo)$')]),
        ),
        migrations.AlterField(
            model_name='customerdetails',
            name='twins',
            field=models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Enter either yes/no', regex='^(?i:yes|yess|yyess|no|noo|nnoo)$')]),
        ),
    ]
