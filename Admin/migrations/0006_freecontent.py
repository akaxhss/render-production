# Generated by Django 3.2.4 on 2023-01-27 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0005_alter_positivecriticalsymptoms_symptom'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('video_url', models.TextField()),
                ('crew', models.CharField(max_length=1000)),
            ],
        ),
    ]