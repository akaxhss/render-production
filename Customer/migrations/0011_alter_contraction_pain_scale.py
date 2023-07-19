# Generated by Django 3.2.4 on 2022-01-13 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0010_auto_20220113_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contraction',
            name='pain_scale',
            field=models.CharField(choices=[('worst pain', 'worst_pain'), ('severe', 'severe'), ('modertae', 'moderate'), ('mild', 'mild'), ('no pain', 'no_pain')], default='no pain', max_length=20),
        ),
    ]