# Generated by Django 3.2.7 on 2021-10-26 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_userprofile_user_mobile_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='forgot_password',
            field=models.TextField(blank=True, null=True),
        ),
    ]
