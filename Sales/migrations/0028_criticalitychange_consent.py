# Generated by Django 3.2.4 on 2021-10-19 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0027_alter_criticalitychange_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='criticalitychange',
            name='consent',
            field=models.BooleanField(default=False),
        ),
    ]