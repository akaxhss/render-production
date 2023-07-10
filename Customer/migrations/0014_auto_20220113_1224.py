# Generated by Django 3.2.4 on 2022-01-13 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0013_alter_contraction_pain_scale'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contraction',
            name='pain_scale',
        ),
        migrations.AddField(
            model_name='contraction',
            name='painScale',
            field=models.CharField(choices=[('worst pain', 'worst pain'), ('severe', 'severe'), ('moderate', 'moderate'), ('mild', 'mild'), ('no pain', 'no pain')], default='no pain', max_length=20),
        ),
    ]
