# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 21:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideshare_profile', '0003_auto_20160502_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='carseat',
            field=models.IntegerField(),
        ),
    ]
