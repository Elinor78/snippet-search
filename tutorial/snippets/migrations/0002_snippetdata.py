# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SnippetData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.CharField(max_length=100)),
                ('field_value', models.CharField(max_length=100)),
                ('owner', models.ForeignKey(related_name='snippetdata', to=settings.AUTH_USER_MODEL)),
                ('snippet', models.ForeignKey(to='snippets.Snippet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
