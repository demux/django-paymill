# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

from .base import PaymillModel
from .transaction import Transaction
from .choices import *


@python_2_unicode_compatible
class Refund(PaymillModel):
    response_code = models.PositiveIntegerField()
    transaction = models.ForeignKey(Transaction, related_name='refunds')
    amount = models.PositiveIntegerField()
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=16)
    description = models.TextField(blank=True)
    livemode = models.BooleanField(default=False)

    def __str__(self):
        return 'Refund - %s' % self.status
