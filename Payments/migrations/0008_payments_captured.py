# Generated by Django 3.2.4 on 2021-08-10 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0007_payments_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='captured',
            field=models.BooleanField(default=False),
        ),
    ]