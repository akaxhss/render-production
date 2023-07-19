# Generated by Django 3.2.4 on 2022-01-13 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Consultant', '0003_delete_messages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customizedplan',
            name='module',
        ),
        migrations.AddField(
            model_name='customizedplan',
            name='tracker',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'diet'), (2, 'activity')], null=True),
        ),
    ]
