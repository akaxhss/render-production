# Generated by Django 3.2.4 on 2021-12-31 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0092_auto_20211222_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default='example@email.com', max_length=300, unique=True),
        ),
    ]
