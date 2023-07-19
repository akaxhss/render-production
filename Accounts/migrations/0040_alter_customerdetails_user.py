# Generated by Django 3.2.4 on 2021-07-12 06:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0039_doctordetails_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdetails',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_details', to=settings.AUTH_USER_MODEL),
        ),
    ]