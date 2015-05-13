# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Lists_to_RDFs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link_name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': 'Referenced Link',
                'verbose_name_plural': 'Referenced Links',
            },
        ),
        migrations.AddField(
            model_name='wikilist',
            name='summary',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wikilist',
            name='url',
            field=models.URLField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='wiki_list',
            field=models.ForeignKey(to='Lists_to_RDFs.WikiList'),
        ),
    ]
