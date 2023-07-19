# Generated by Django 3.2.4 on 2022-01-03 05:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointments', '0011_appointments_schedule'),
        ('Payments', '0024_remove_subscriptions_payments'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('amount', models.IntegerField(default=0)),
                ('order_id', models.CharField(default='', max_length=400)),
                ('payment_id', models.CharField(default='', max_length=400)),
                ('signature', models.CharField(default='', max_length=400)),
                ('captured', models.BooleanField(default=False)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Appointments.appointments')),
            ],
        ),
    ]
