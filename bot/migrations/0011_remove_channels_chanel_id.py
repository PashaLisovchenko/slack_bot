# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-03 19:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0010_auto_20171203_1845'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channels',
            name='chanel_id',
        ),
    ]
