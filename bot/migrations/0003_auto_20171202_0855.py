# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-02 08:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bot', '0002_auto_20171202_0852'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='moderators',
        ),
        migrations.AddField(
            model_name='team',
            name='users',
            field=models.ManyToManyField(related_name='users_team', to=settings.AUTH_USER_MODEL),
        ),
    ]