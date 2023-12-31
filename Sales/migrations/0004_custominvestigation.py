# Generated by Django 3.2.4 on 2021-07-08 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0003_auto_20210708_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomInvestigation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, null=True)),
                ('value', models.CharField(max_length=500, null=True)),
                ('normal_range', models.CharField(max_length=500, null=True)),
                ('investigation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Sales.investigation')),
            ],
        ),
    ]
