# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from ..models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    holder = serializers.CharField(source='_holder', read_only=True)
    fa_icon = serializers.CharField(read_only=True)
    masked = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'type', 'client', 'card_type', 'holder', 'fa_icon',
                  'masked', 'created_at')
