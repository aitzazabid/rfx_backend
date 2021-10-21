# Generated by Django 3.2.7 on 2021-10-21 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_childsubcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='company_brand',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='company_size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='company_type',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_mobile_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='year_of_establishment',
            field=models.IntegerField(default=0),
        ),
    ]
