# Generated by Django 3.2.4 on 2021-08-08 04:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0055_alter_customerdetails_consultant'),
        ('Appointments', '0005_rename_rescheduled_by_doctor_appointments_rescheduled_by_consultant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointments',
            old_name='rescheduled_by_consultant',
            new_name='rescheduled_by_doctor',
        ),
        migrations.AddField(
            model_name='appointments',
            name='doctor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Accounts.doctordetails'),
        ),
        migrations.AlterUniqueTogether(
            name='appointments',
            unique_together={('date', 'customer', 'doctor')},
        ),
        migrations.RemoveField(
            model_name='appointments',
            name='consultant',
        ),
    ]