# Generated by Django 3.2.4 on 2021-12-07 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0088_alter_doctordetails_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctordetails',
            name='profile_img',
            field=models.FileField(blank=True, null=True, upload_to='ProfilePic/'),
        ),
    ]
