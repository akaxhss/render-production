# Generated by Django 3.2.4 on 2022-02-04 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0031_alter_customercallreposnses_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigationcriticallity',
            name='criticality',
            field=models.IntegerField(default=0),
        ),
    ]
