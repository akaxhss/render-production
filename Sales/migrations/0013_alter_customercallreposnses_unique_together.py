# Generated by Django 3.2.4 on 2021-08-16 06:16

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Sales', '0012_auto_20210816_1144'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customercallreposnses',
            unique_together={('customer', 'date')},
        ),
    ]
