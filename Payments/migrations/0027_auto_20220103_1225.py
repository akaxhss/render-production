# Generated by Django 3.2.4 on 2022-01-03 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointments', '0011_appointments_schedule'),
        ('Payments', '0026_auto_20220103_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointmentpayments',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='appointmentpayments',
            name='doctor',
        ),
        migrations.AddField(
            model_name='appointmentpayments',
            name='appointment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_appointment', to='Appointments.appointments'),
        ),
    ]