# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0002_snippetdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippetdata',
            name='snippet',
            field=models.ForeignKey(related_name='data', to='snippets.Snippet'),
            preserve_default=True,
        ),
    ]
