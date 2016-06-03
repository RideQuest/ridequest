# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-01 00:01
from __future__ import unicode_literals

from django.db import migrations, models
import rideshare_profile.models


class Migration(migrations.Migration):

    dependencies = [
        ('rideshare_profile', '0005_profile_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to=rideshare_profile.models.upload_to),
        ),
    ]
