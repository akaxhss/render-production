# Generated by Django 3.2.4 on 2022-02-04 04:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0032_investigationcriticallity_criticality'),
        ('Customer', '0020_alter_activitymainmodule_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='symptoms',
            name='criticality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Sales.investigationcriticallity'),
        ),
    ]
