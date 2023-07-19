# Generated by Django 3.2.4 on 2021-08-07 11:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0054_auto_20210807_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdetails',
            name='consultant',
            field=models.ManyToManyField(blank=True, related_name='consultants', to=settings.AUTH_USER_MODEL),
        ),
    ]
