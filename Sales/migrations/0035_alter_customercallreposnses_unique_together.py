# Generated by Django 3.2.4 on 2023-07-21 10:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Sales', '0034_alter_customercallreposnses_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customercallreposnses',
            unique_together={('customer', 'date')},
        ),
    ]
