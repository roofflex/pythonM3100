# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-10 13:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0013_auto_20170410_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
