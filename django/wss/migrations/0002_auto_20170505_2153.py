# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-06 00:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wss', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveychoice',
            name='score',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]