# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url

from .views import PaymillTransactionView, PaymillAddCardView, WebhookView


urlpatterns = patterns('',
    url(r'^transaction/$', PaymillTransactionView.as_view(), name='paymill-payment'),
    url(r'^addcard/$', PaymillAddCardView.as_view(), name='paymill-add-card'),
    url(r'^webhook/$', WebhookView.as_view(), name='paymill-webhook'),
)
