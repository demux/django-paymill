# -*- coding: utf-8 -*-
from __future__ import unicode_literals


INTERVAL_CHOICES = (
    ('1 DAY',   'Daily'),
    ('1 WEEK',  'Weekly'),
    ('2 WEEK',  'Bimonthly'),
    ('1 MONTH', 'Monthly'),
    ('3 MONTH', 'Quarterly'),
    ('6 MONTH', 'Biannual'),
    ('1 YEAR',  'Annual'),
)

CURRENCY_CHOICES = (
    ('EUR', 'Euro'),
    ('ISK', 'Icelandic Krona'),
    ('USD', 'US Dollar'),
    ('GBP', 'Pound'),
)