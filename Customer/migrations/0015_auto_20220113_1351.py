# Generated by Django 3.2.4 on 2022-01-13 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0014_auto_20220113_1224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='symptomsinput',
            name='report',
        ),
        migrations.AddField(
            model_name='symptomsinput',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=100, null=True),
        ),
    ]
