# Generated by Django 3.2.7 on 2021-10-26 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20211022_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user_mobile_number',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
