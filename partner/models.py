# -*- coding: utf-8 -*-
# import logging
from decimal import *

from django.db import models
from django.db.models import Sum

# from django.core.cache import cache
from django.contrib.auth.models import User

from main.models import Payment


class PartnerManager(models.Manager):
    def get_by_user(self, user):
        return self.filter(user=user)


class Partner(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    secret_code = models.CharField(max_length=16)
    pay_share = models.DecimalField(max_digits=3, decimal_places=2)

    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    address = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=10)
    contact = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    info = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PartnerManager()

    # def __getattr__(self, name):
    # 	if name == 'used':
    # 		if len(self.use) == 0: return []
    # 		return self.use.split(',')
    # 	else:
    # 		return self.__getattribute__(name)

    def save(self):
        if self.id is None and self.secret_code == '': self.secret_code = self.generate_secret_code()
        super(Partner, self).save()

    def unicode(self):
        return 'Partner %s (%s)' % (self.name, self.user)

    def generate_secret_code(self):
        return User.objects.make_random_password(length=16, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')

    class Meta:
        db_table = 'partner'
        verbose_name = 'Partner'


class PartnerPaymentManager(models.Manager):
    def get_by_partner(self, partner):
        return self.filter(partner=partner).filter(is_payable=True, is_fraud=False).order_by('-created_at')

    def get_total_by_partner(self, partner, only_unpayed=True):
        pp = self.filter(partner=partner, is_payable=True, is_fraud=False)
        if only_unpayed:
            pp = pp.filter(is_payed=False)

        value = pp.aggregate(total=Sum('amount'))['total']
        if value is None:
            return 0
        else:
            if value >= Decimal('0.1'):
                getcontext().prec = 1
            elif value >= Decimal('0.01'):
                getcontext().prec = 2
            return Decimal(value * Decimal('1'))

        return pp.aggregate(total=Sum('amount'))['total']


class PartnerPayment(models.Model):
    partner = models.ForeignKey(Partner)
    payment = models.ForeignKey(Payment)
    amount = models.DecimalField(max_digits=7, decimal_places=3)
    share = models.DecimalField(max_digits=3, decimal_places=2)

    is_payable = models.BooleanField(default=True)
    is_payed = models.BooleanField(default=False)
    is_fraud = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PartnerPaymentManager()

    # def __getattr__(self, name):
    # 	if name == 'used':
    # 		if len(self.use) == 0: return []
    # 		return self.use.split(',')
    # 	else:
    # 		return self.__getattribute__(name)

    def unicode(self):
        return 'Partner\'s payment of %s (%s%%)' % (self.amount, (self.share * 100))

    class Meta:
        db_table = 'partner_payment'
        verbose_name = 'Partner Payment'
