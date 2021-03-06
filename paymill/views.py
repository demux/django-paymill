# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pickle
import json
import pymill

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django.views.generic import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .signals import get_signal
from .models import *

from paymill.webhooks import validate_webhook

class PaymillTransactionView(View):
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('payment_amount', 0)
        currency = request.POST.get('payment_currency', 'USD')
        description = request.POST.get('payment_description', '')
        offer = request.POST.get('payment_subscription_code', '')
        email = request.POST.get('payment_client_email', '')
        name = request.POST.get('payment_client_name', '')
        next = request.POST.get(
            'next', getattr(settings, 'PAYMILL_SUCCESS', '/'))

        p = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)
        #we create this in any case
        client = p.new_client(email, name)
        card = p.new_card(request.POST.get('paymillToken'), client.id)

        if offer:
            paymill_offer = Offer.objects.get(id=offer)
            client = Client.update_or_create(client)
            payment = Payment.update_or_create(card)
            paymill_offer.subscribe(client)
        else:
            transaction = p.transact(
                amount=amount,
                currency=currency,
                description=description,
                payment=card
            )

            if getattr(settings, 'PAYMILL_SAVE_TRANSACTIONS', True):
                transaction = Transaction.parse_transaction(transaction)

        return HttpResponseRedirect(next)


class PaymillAddCardView(View):
    def post(self, request, *args, **kwargs):
        next = request.POST.get(
            'next', getattr(settings, 'PAYMILL_SUCCESS', '/'))
        client = request.session.get('paymill_client', None)
        client.add_payment(request.POST.get('paymillToken'))

        return HttpResponseRedirect(next)


class WebhookView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WebhookView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        #if validate_webhook(kwargs.pop('secret')):
        try:
            event = json.loads(request.body)
            # TODO: Check for edge cases and handle errors
            event = event['event']
            event_name = event['event_type'].replace('.', '_')

            # Process Paymill objects
            f = getattr(self, event_name, None)

            if f:
                f(event)
            signal = get_signal(event_name)
            signal.send(sender=self, event=event)
        except Exception as e:
            print 'ERROR: ' + unicode(e)
            pass  # TODO: Log errors

        # Paymill doesn't care if we succeed or fail so we return an empty
        # 200:OK
        return HttpResponse()

    def transaction_created(self, event):
        t = Transaction.update_or_create(event['event_resource'])
        t.save()

    def transaction_succeeded(self, event):
        self.transaction_created(event)

    def transaction_failed(self, event):
        self.transaction_created(event)

    def refund_created(self, event):
        r = Refund.update_or_create(event['event_resource'])
        r.save()

    def refund_succeeded(self, event):
        self.refund_created(event)

    def refund_failed(self, event):
        self.refund_created(event)

    def client_updated(self, event):
        c = Client.update_or_create(event['event_resource'])
        c.save()

    def subscription_created(self, event):
        self.subscription_updated(event)

    def subscription_updated(self, event):
        s = Subscription.update_or_create(event['event_resource'])
        s.save()

    def subscription_deleted(self, event):
        s = Subscription.objects.get(pk=event['event_resource']['id'])
        s.delete()

'''
    {
        "event":{
            "event_type":"client.updated",
            "event_resource":{
                "id":"client_cdcc9709ffcef07f9286",
                "email":"ulfurk@ulfurk.com",
                "description":"Ulfur Kristjansson (Are we cooking with gas?)",
                "created_at":1388418081,
                "updated_at":1388831265,
                "app_id":null,
                "payment":[],
                "subscription":null
            },
            "created_at":1388831265,
            "app_id":null
        }
    }
'''
