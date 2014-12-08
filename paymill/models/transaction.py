# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

from .base import PaymillModel
from .client import Client
from .payment import Payment
from .choices import *


@python_2_unicode_compatible
class Transaction(PaymillModel):
    status = models.CharField(max_length=16)
    response_code = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)

    livemode = models.BooleanField(default=False)
    origin_amount = models.PositiveIntegerField()

    payment = models.ForeignKey(Payment, related_name='transactions')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    amount = models.CharField(max_length=10)
    client = models.ForeignKey(Client, related_name='transactions')

    @property
    def refunded(self):
        '''Total refunded amount in CENTS'''
        res = self.refunds.aggregate(models.Sum('amount'))
        return res['amount__sum'] or 0

    def __str__(self):
        return '%s - %s' % (self.payment, self.status)

    @classmethod
    def parse_transaction(cls, t):
        client = Client.update_or_create(t.client)
        payment = Payment.update_or_create(t.payment)
        transaction = Transaction.update_or_create(t)

        return transaction
