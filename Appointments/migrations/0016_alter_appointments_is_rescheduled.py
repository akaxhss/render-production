# Generated by Django 3.2.4 on 2023-07-23 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointments', '0015_alter_appointments_is_rescheduled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='is_rescheduled',
            field=models.BooleanField(default=False),
        ),
    ]