# Generated by Django 3.2.4 on 2021-09-18 04:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0070_alter_user_is_email_verified'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_email_verified',
            new_name='is_otp_verified',
        ),
    ]
