# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-02 19:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_auto_20171202_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='slug',
            field=models.SlugField(max_length=20, null=True),
        ),
    ]