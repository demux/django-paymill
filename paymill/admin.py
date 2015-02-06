# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime
import pymill
from django.contrib import admin
from django import forms
from django.conf import settings

from .models import *


class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'description', 'id', 'created_at')
    search_fields = ('email', )
    fieldsets = (
        (None, {
            'fields': (
                'email',
                'description',
                'payments_',
            )
        }),
        ('Advanced', {
            'fields': (
                'id',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse', 'collapse-closed'),
        })
    )
    readonly_fields = (
        'email',
        'description',
        'payments_',

        'id', 'created_at', 'updated_at',
    )

    def payments_(self, obj):
        s = []
        for p in obj.payments.all().order_by('-created_at'):
            s.append('<a href="{}">{}</a> <span style="color:grey">({})</span>'.format(
                p.get_admin_url(),
                p.__str__(),
                p.created_at.strftime('%c'),
            ))
        return '\n'.join(s)
    payments_.allow_tags=True


class PaymentAdminForm(forms.ModelForm):
    transaction_amount = forms.IntegerField(label='Amount', required=False,
        help_text='Transaction amount in CENTS (1 becomes 100).')
    transaction_currency = forms.ChoiceField(label='Currency', required=False,
                                             choices=CURRENCY_CHOICES)
    transaction_description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 2}),
    )

    class Meta:
        model = Payment
        exclude = []


class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm

    list_display = ('card_holder', 'last4', 'id', 'created_at')
    search_fields = ('card_holder', 'last4')
    fieldsets = (
        (None, {
            'fields': (
                ('client', 'type'),
                ('card_type', 'last4'),
                ('expire_month', 'expire_year'),
                ('card_holder', 'country'),
            )
        }),
        ('Create a new Transaction', {
            'fields': (
                'transaction_amount',
                'transaction_currency',
                'transaction_description',
            )
        }),
        ('Transactions', {
            'fields': (
                'transactions_',
            )
        }),
        ('Advanced', {
            'fields': (
                'id',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse', 'collapse-closed'),
        })
    )
    readonly_fields = (
        'type',
        'card_type', 'last4',
        'expire_month', 'expire_year',
        'card_holder', 'country', 'transactions_',

        'id', 'client', 'created_at', 'updated_at',
    )

    def transactions_(self, obj):
        s = []
        for t in obj.transactions.all().order_by('-created_at'):
            s.append('<a href="{}">{}</a> [<b>{:20,.2f}</b> {} ] <span style="color:grey">({})</span>'.format(
                t.get_admin_url(),
                t.__str__(),
                t.origin_amount / 100,
                t.currency,
                t.created_at.strftime('%c'),
            ))
        return '\n'.join(s)
    transactions_.allow_tags=True

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            d = form.cleaned_data
            p = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)

            if d['transaction_amount']:
                _transaction = p.transact(
                    payment=obj.id,
                    amount=d['transaction_amount'],
                    description=d['transaction_description'],
                    currency=d['transaction_currency'],
                    client=obj.client.id,
                )
                Transaction.parse_transaction(_transaction)


class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'amount', 'currency', 'interval', 'id', 'created_at')
    search_fields = ('name', )
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug'),
                ('amount', 'currency'),
                ('interval', 'trial_period_days'),
            )
        }),
        ('Advanced', {
            'fields': (
                'id',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse', 'collapse-closed'),
        })
    )
    readonly_fields = ('id', 'slug', 'created_at', 'updated_at', )


class TransactionAdminForm(forms.ModelForm):
    refund = forms.IntegerField(required=False,
        help_text='Refund transaction by the defined amount in CENTS (1 becomes 100).')

    def clean_refund(self):
        amount = self.cleaned_data['refund']
        if amount > self.instance.origin_amount - self.instance.refunded:
            raise forms.ValidationError('Refund value too high.')
        return amount

    class Meta:
        model = Transaction
        exclude = []


class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            d = form.cleaned_data
            p = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)

            if d['refund']:
                refund = p.refund(obj.id, d['refund'])
                Refund.update_or_create(refund)

    list_filter = ['status', 'response_code']

    list_display = ['payment', 'status', 'original_amount', 'refunded_total']

    exclude = ['livemode', 'amount', 'client']

    fieldsets = (
        (None, {
            'fields': (
                ('status', 'response'),
                ('original_amount', 'total_amount'),
                'payment',
                'description',
            )
        }),
        ('Refund', {
            'fields': (
                'refund',
                'refunds_',
                'refunded_total',
            )
        }),
        ('Advanced', {
            'fields': (
                'id',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse', 'collapse-closed'),
        })
    )
    readonly_fields = (
        'status',
        'response',
        'original_amount',
        'total_amount',
        'payment',
        'description',
        'refunded_total',
        'refunds_',

        'id', 'created_at', 'updated_at',
    )

    def original_amount(self, obj):
        try:
            return '{:20,.2f} {}'.format(obj.origin_amount / 100, obj.currency)
        except TypeError:
            return ''

    def total_amount(self, obj):
        try:
            return '{:20,.2f} {}'.format(
                (obj.origin_amount - obj.refunded) / 100, obj.currency)
        except TypeError:
            return ''

    def refunded_total(self, obj):
        try:
            return '{:20,.2f} {}'.format(obj.refunded / 100, obj.currency)
        except TypeError:
            return ''

    def refunds_(self, obj):
        s = []
        for r in obj.refunds.all().order_by('-created_at'):
            s.append('{} <b>{:20,.2f}</b> {} <span style="color:grey">({})</span>'.format(
                r.get_status_display(),
                r.amount / 100,
                obj.currency,
                r.updated_at.strftime('%c'),
            ))
        return '\n'.join(s)
    refunds_.allow_tags=True

    def response(self, obj):
        p = pymill.Pymill(settings.PAYMILL_PRIVATE_KEY)
        return '%s (%s)' % (p.response_code2text(obj.response_code), obj.response_code)


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Subscription)
