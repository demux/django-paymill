# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import uuid
from urlparse import urlparse
from django.core.urlresolvers import reverse, resolve
from django.conf import settings

from pymill import Pymill

WEBHOOK_EVENTS = (
    'chargeback.executed',
    'refund.created',
    'refund.succeeded',
    'refund.failed',
    'subscription.created',
    'subscription.updated',
    'subscription.deleted',
    'subscription.succeeded',
    'subscription.failed',
    'transaction.created',
    'transaction.succeeded',
    'transaction.failed',
    'app.merchant.activated',
    'invoice.available',
    'payout.transferred',
    'app.merchant.deactivated',
    'app.merchant.rejected',
    'client.updated',
    'app.merchant.app.disabled'
)


def get_webhook():
    paymill = Pymill(settings.PAYMILL_PRIVATE_KEY)
    webhooks = paymill.get_webhooks()
    for hook in webhooks:
        url = urlparse(hook.url)
        try:
            match = resolve(url.path)
            if match.url_name == 'paymill-webhook':
                return match.kwargs.get('secret', None)
        except:
            pass
    return None


def validate_webhook(secret):
    return secret == get_webhook()


def install_webhook():
    paymill = Pymill(settings.PAYMILL_PRIVATE_KEY)
    secret = uuid.uuid4().hex
    path = reverse('paymill-webhook', args=[secret])
    url = ''.join([settings.PAYMILL_WEBHOOK_HOST, path])
    paymill.new_webhook(url, WEBHOOK_EVENTS)
    return secret


def init_webhook():
    print 'Looking for webhook'
    secret = get_webhook()
    if not secret:
        print 'Webhook not found, installing'
        secret = install_webhook()
    print 'Webhook ready: %s' % secret

    return secret
