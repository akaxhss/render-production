# Generated by Django 3.2.4 on 2022-02-25 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Analytics', '0004_auto_20220202_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalhistory',
            name='category',
            field=models.CharField(blank=True, choices=[('Personal Details', 'Personal Details'), ('Medical history', 'Medical Details'), ('Family History', 'Family Details'), ('Life Style', 'Life Style')], max_length=20, null=True),
        ),
    ]
