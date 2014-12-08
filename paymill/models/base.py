# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

import pytz
utc = pytz.UTC

from pymill import Pymill, PaymillObject


def paymill_dict(ob):
    if isinstance(ob, PaymillObject):
        return ob.__dict__
    elif isinstance(ob, dict):
        return ob
    raise TypeError('paymill_dict expects either PaymillObject or dict')


class PaymillModel(models.Model):
    paymill = Pymill(settings.PAYMILL_PRIVATE_KEY)

    id = models.CharField(max_length=80, db_index=True, primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.module_name)
        # Underscores need to be replaced:
        pk = self.pk.replace('_', '_5F')
        return reverse('admin:%s_%s_change' % info, args=(pk,))

    class Meta:
        app_label = 'paymill'
        abstract = True
        ordering = ['-created_at']

    def _update_from_paymill_object(self, ob):
        # Make sure we have a dict rather than a PaymillObject (from Pymill)
        ob = paymill_dict(ob)
        # Nothing has been updated yet
        updated = False
        # Iterate over all the items of the object dict
        for k, v in ob.items():
            # If this model has this field and the value is not None
            if v is not None and (hasattr(self, k) or hasattr(self, '%s_id' % k)):
                # Let's type check the field
                ftype = self._meta.get_field(k)
                # If the field is a DateTimeField ...
                if isinstance(ftype, models.DateTimeField):
                    # we know the value must be a datetime object
                    v = datetime.utcfromtimestamp(float(v))
                    v = utc.localize(v)
                # If the field is a ForeignKey ...
                if isinstance(ftype, models.ForeignKey):
                    # we know the value is an object-id and we must use the
                    # corresponding field name
                    k = '%s_id' % k
                    # What we have might not be the actual id of the object
                    if isinstance(v, dict):
                        # but a dict containing all its' attributes
                        v = v['id']

                # If the current value and the new value differ ...
                if getattr(self, k) != v:
                    # set the current value to the new value
                    setattr(self, k, v)
                # Have we updated anything yet?
                updated = updated or getattr(self, k) != v
        # Let the caller know if anything got updated
        return updated

    def _create_paymill_object(self, *args, **kwargs):
        raise NotImplementedError(
            '_create_paymill_object not implemented for this class')

    def save(self, *args, **kwargs):
        if not self.id:
            ob = self._create_paymill_object()
            if ob:
                self.id = ob.id
                self._update_from_paymill_object(ob)
        return super(PaymillModel, self).save(*args, **kwargs)

    def _delete_paymill_object(self):
        raise NotImplementedError(
            '_delete_paymill_object not implemented for this class')

    def delete(self, *args, **kwargs):
        self._delete_paymill_object()
        return super(PaymillModel, self).delete(*args, **kwargs)

    @classmethod
    def update_or_create(cls, ob):
        ob = paymill_dict(ob)
        created = False
        try:
            djob = cls.objects.get(id=ob['id'])
        except (cls.DoesNotExist, KeyError) as e:
            djob = cls()
            created = True

        djob._update_from_paymill_object(ob)
        djob.save()
        return djob
