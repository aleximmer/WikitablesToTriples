# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Lists_to_RDFs', '0002_auto_20150511_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiTable',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('html', models.TextField()),
                ('checked', models.BooleanField(default=False)),
                ('algo_col', models.CharField(null=True, blank=True, max_length=128)),
                ('hum_col', models.CharField(null=True, blank=True, max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='wikilist',
            name='base_title',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wikilist',
            name='has_tables',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wikitable',
            name='wiki_list',
            field=models.ForeignKey(to='Lists_to_RDFs.WikiList'),
        ),
    ]
