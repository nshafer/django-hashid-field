# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import hashid_field.field


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', hashid_field.field.HashidAutoField(min_length=7, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.ForeignKey(to='library.Author', blank=True, null=True, related_name='books'),
        ),
        migrations.AddField(
            model_name='book',
            name='editors',
            field=models.ManyToManyField(to='library.Editor'),
        ),
    ]
