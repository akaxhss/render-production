# Generated by Django 3.2.4 on 2023-08-08 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0122_alter_customerdetails_referalid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdetails',
            name='referalId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referal_doc', to='Accounts.doctordetails'),
        ),
    ]
