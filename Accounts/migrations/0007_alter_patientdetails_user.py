# Generated by Django 3.2.4 on 2021-06-14 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0006_auto_20210614_0728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientdetails',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Accounts.user'),
        ),
    ]
