# Generated by Django 3.2.7 on 2021-10-28 16:51

from django.db import migrations

from django.contrib.postgres import operations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_fuzzysearch'),
    ]

    operations = [
        operations.TrigramExtension(),
    ]