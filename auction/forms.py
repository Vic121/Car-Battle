# -*- coding: utf-8 -*-

from django import forms


class SellForm(forms.Form):
    DURATION = (
        (1, "1 %s" % 'day',),
        (2, "2 %s" % 'days',),
        (3, "3 %s" % 'days',),
        (4, "4 %s" % 'days',),
        (5, "5 %s" % 'days',),
        (6, "6 %s" % 'days',),
        (7, "7 %s" % 'days',),
    )

    # extra_title = forms.CharField(required=False, max_length=20)
    start_price = forms.IntegerField(required=False, max_value=99999999, widget=forms.TextInput(attrs={'size': '7'}))
    buy_it_now_price = forms.IntegerField(required=False, max_value=99999999,
                                          widget=forms.TextInput(attrs={'size': '7'}))
    duration = forms.ChoiceField(choices=DURATION)
