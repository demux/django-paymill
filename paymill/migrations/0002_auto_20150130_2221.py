# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paymill', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='client',
            field=models.ForeignKey(related_name='payments', blank=True, to='paymill.Client', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='refund',
            name='transaction',
            field=models.ForeignKey(related_name='refunds', to='paymill.Transaction'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='subscription',
            name='client',
            field=models.ForeignKey(related_name='subscriptions', to='paymill.Client'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='subscription',
            name='offer',
            field=models.ForeignKey(related_name='subscriptions', to='paymill.Offer'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='subscription',
            name='payment',
            field=models.ForeignKey(related_name='subscriptions', to='paymill.Payment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='client',
            field=models.ForeignKey(related_name='transactions', to='paymill.Client'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment',
            field=models.ForeignKey(related_name='transactions', to='paymill.Payment'),
            preserve_default=True,
        ),
    ]
