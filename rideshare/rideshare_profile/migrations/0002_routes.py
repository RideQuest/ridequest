# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 20:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rideshare_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Routes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line1', models.CharField(max_length=40, verbose_name='Address line 1')),
                ('address_line2', models.CharField(blank=True, max_length=40, verbose_name='Address line 2')),
                ('postal_code', models.CharField(max_length=10, verbose_name='Zip Code')),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=40, verbose_name='State')),
                ('destination_address_line1', models.CharField(max_length=40, verbose_name='Address line 1')),
                ('destination_address_line2', models.CharField(blank=True, max_length=40, verbose_name='Address line 2')),
                ('destination_postal_code', models.CharField(max_length=10, verbose_name='Zip Code')),
                ('destination_city', models.CharField(max_length=50)),
                ('destination_state', models.CharField(max_length=40, verbose_name='State')),
                ('in_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='rideshare_profile.Profile')),
            ],
        ),
    ]