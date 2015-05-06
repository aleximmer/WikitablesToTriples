# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RDF',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('statement', models.TextField()),
            ],
            options={
                'verbose_name': 'RDF statement',
                'verbose_name_plural': 'RDF statements',
            },
        ),
        migrations.CreateModel(
            name='WikiList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('html', models.TextField()),
            ],
            options={
                'verbose_name': 'Wikipedia List',
                'verbose_name_plural': 'Wikipedia Lists',
            },
        ),
        migrations.AddField(
            model_name='rdf',
            name='wiki_list',
            field=models.ForeignKey(to='Lists_to_RDFs.WikiList'),
        ),
    ]
