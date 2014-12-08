# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from .base import PaymillModel


class Client(PaymillModel):
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def _create_paymill_object(self):
        '''Creates a new Client on the Paymill servers and returns the json object'''
        return self.paymill.new_client(self.email, self.description)

    def _delete_paymill_object(self):
        # We need to cancel all subscriptions before we can delete the client
        for sub in self.subscriptions.all():
            sub.cancel()
        for payment in self.payments.all():  # Let's also remove all his cards
            payment.delete()
        # Finally we can safely delete the client
        self.paymill.delete_client(self.id)

    def get_payment(self, i=0):
        pms = self.payments.all()
        if len(pms) > i:
            return pms[i]
        return None

    def add_payment(self, token):
        p = self.payments.create(token=token, client=self)
        p.save()
        return p

    @property
    def has_payment(self):
        return self.get_payment() is not None

    def __unicode__(self):
        return u'%s - "%s"' % (self.email, self.description)
