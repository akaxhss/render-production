# Generated by Django 3.2.4 on 2021-07-01 03:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0021_auto_20210701_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctordetails',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='docDetails', to=settings.AUTH_USER_MODEL),
        ),
    ]
