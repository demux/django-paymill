# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

from .base import PaymillModel
from .client import Client


@python_2_unicode_compatible
class Payment(PaymillModel):
    TYPE_CHOICES = (
        ('creditcard', 'Credit Card'),
        ('debit', 'Debit Card'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    client = models.ForeignKey(Client, related_name='payments',
                               null=True, blank=True)

    # For Credit Cards only:
    CARD_TYPE_CHOICES = (
        ('visa', 'VISA'),
        ('mastercard', 'Master Card'),
    )
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES,
                                 blank=True)

    country = models.CharField(max_length=100, blank=True)
    expire_month = models.PositiveIntegerField(blank=True, null=True)
    expire_year = models.PositiveIntegerField(blank=True, null=True)
    card_holder = models.CharField(max_length=100, blank=True)
    last4 = models.CharField(max_length=4, blank=True)

    # For Debit Cards only:
    code = models.CharField(max_length=100, blank=True)
    account = models.CharField(max_length=100, blank=True)
    holder = models.CharField(max_length=100, blank=True)
    iban = models.CharField(max_length=100, blank=True)
    bic = models.CharField(max_length=100, blank=True)

    # Methods:
    _token = None

    def __init__(self, *args, **kwargs):
        self._token = kwargs.pop('token', None)
        return super(Payment, self).__init__(*args, **kwargs)

    def _create_paymill_object(self):
        if self._token:
            return self.paymill.new_card(
                self._token,
                client=self.client.id if self.client else None
            )
        return None

    def _delete_paymill_object(self, *args, **kwargs):
        self.paymill.delete_card(self.id)

    def __str__(self):
        if self.type == 'creditcard':
            return 'Credit Card - %s - %s (**** ***** **** %s)' % (
                self.card_holder, self.card_type, self.last4)
        elif self.type == 'debit':
            num = self.iban or self.account
            code = self.bic or self.code
            return 'Debit Card - %s - %s - %s' % (self.holder, num, code)
