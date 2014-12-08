# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True, db_index=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('description', models.TextField(null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True, db_index=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('name', models.CharField(max_length=50)),
                ('amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=3, choices=[('EUR', 'Euro'), ('ISK', 'Icelandic Krona'), ('USD', 'US Dollar'), ('GBP', 'Pound')])),
                ('interval', models.CharField(max_length=20, choices=[('1 DAY', 'Daily'), ('1 WEEK', 'Weekly'), ('2 WEEK', 'Bimonthly'), ('1 MONTH', 'Monthly'), ('3 MONTH', 'Quarterly'), ('6 MONTH', 'Biannual'), ('1 YEAR', 'Annual')])),
                ('trial_period_days', models.PositiveIntegerField(blank=True)),
                ('slug', models.SlugField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True, db_index=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('type', models.CharField(max_length=10, choices=[('creditcard', 'Credit Card'), ('debit', 'Debit Card')])),
                ('card_type', models.CharField(blank=True, max_length=10, choices=[('visa', 'VISA'), ('mastercard', 'Master Card')])),
                ('country', models.CharField(max_length=100, blank=True)),
                ('expire_month', models.PositiveIntegerField(null=True, blank=True)),
                ('expire_year', models.PositiveIntegerField(null=True, blank=True)),
                ('card_holder', models.CharField(max_length=100, blank=True)),
                ('last4', models.CharField(max_length=4, blank=True)),
                ('code', models.CharField(max_length=100, blank=True)),
                ('account', models.CharField(max_length=100, blank=True)),
                ('holder', models.CharField(max_length=100, blank=True)),
                ('iban', models.CharField(max_length=100, blank=True)),
                ('bic', models.CharField(max_length=100, blank=True)),
                ('client', models.ForeignKey(blank=True, to='paymill.Client', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True, db_index=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('response_code', models.PositiveIntegerField()),
                ('amount', models.PositiveIntegerField()),
                ('status', models.CharField(max_length=16, choices=[('open', 'Open'), ('pending', 'Pending'), ('refunded', 'Refunded')])),
                ('description', models.TextField(blank=True)),
                ('livemode', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True, db_index=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('livemode', models.BooleanField(default=False)),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('trial_start', models.DateTimeField(null=True, blank=True)),
                ('trial_end', models.DateTimeField(null=True, blank=True)),
                ('next_capture_at', models.DateTimeField()),
                ('canceled_at', models.DateTimeField(null=True, blank=True)),
                ('start_at', models.DateTimeField(null=True, blank=True)),
                ('client', models.ForeignKey(to='paymill.Client')),
                ('offer', models.ForeignKey(to='paymill.Offer')),
                ('payment', models.ForeignKey(to='paymill.Payment')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True, db_index=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('status', models.CharField(max_length=16)),
                ('response_code', models.PositiveIntegerField()),
                ('description', models.TextField(null=True, blank=True)),
                ('livemode', models.BooleanField(default=False)),
                ('origin_amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=3, choices=[('EUR', 'Euro'), ('ISK', 'Icelandic Krona'), ('USD', 'US Dollar'), ('GBP', 'Pound')])),
                ('amount', models.CharField(max_length=10)),
                ('client', models.ForeignKey(to='paymill.Client')),
                ('payment', models.ForeignKey(to='paymill.Payment')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='refund',
            name='transaction',
            field=models.ForeignKey(to='paymill.Transaction'),
            preserve_default=True,
        ),
    ]
