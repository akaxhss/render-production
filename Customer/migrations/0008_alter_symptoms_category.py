# Generated by Django 3.2.4 on 2021-11-30 04:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0007_merge_0005_auto_20211125_1100_0006_auto_20211125_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symptoms',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='symptoms', to='Customer.symptomscategory'),
        ),
    ]
