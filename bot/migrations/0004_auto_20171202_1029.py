# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-02 10:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20171202_0855'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='bot_access_token',
        ),
        migrations.RemoveField(
            model_name='team',
            name='bot_user_id',
        ),
    ]
