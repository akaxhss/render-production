# Generated by Django 3.2.4 on 2021-07-12 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0041_doctordetails_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctordetails',
            name='age',
            field=models.IntegerField(default=0),
        ),
    ]