# -*- coding: utf-8 -*-
from django import forms

from partner.models import Partner


class PartnerForm(forms.ModelForm):
    contact = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=25, widget=forms.TextInput, required=False)
    last_name = forms.CharField(max_length=25, widget=forms.TextInput, required=False)
    address = forms.CharField(max_length=50, widget=forms.TextInput, required=False)
    postcode = forms.CharField(max_length=10, widget=forms.TextInput, required=False)
    country = forms.CharField(max_length=10, widget=forms.TextInput, required=False)
    website = forms.URLField(max_length=255, required=True)
    info = forms.CharField(max_length=255, widget=forms.TextInput, required=False)


class PartnerAddForm(forms.ModelForm):
    name = forms.CharField(max_length=20, required=True)
    contact = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=25, widget=forms.TextInput, required=False)
    last_name = forms.CharField(max_length=25, widget=forms.TextInput, required=False)
    address = forms.CharField(max_length=50, widget=forms.TextInput, required=False)
    postcode = forms.CharField(max_length=10, widget=forms.TextInput, required=False)
    country = forms.CharField(max_length=10, widget=forms.TextInput, required=False)
    website = forms.URLField(max_length=255, required=True)
    info = forms.CharField(max_length=255, widget=forms.TextInput, required=False)

    def clean_name(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        try:
            user = Partner.objects.get(name__iexact=self.cleaned_data['name'])
        except Partner.DoesNotExist:
            return self.cleaned_data['name']
        raise forms.ValidationError(u'This name is already taken. Please choose another.')
