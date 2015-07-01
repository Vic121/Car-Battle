# -*- coding: utf-8 -*-

import re

from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput)
    email = forms.EmailField(max_length=20, widget=forms.TextInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        """
        Validates that the username is alphanumeric and is not already
        in use.
        """
        username_re = re.compile(r'^[A-Za-z]{1,}\w*$')

        if 'username' in self.cleaned_data:
            if not username_re.search(self.cleaned_data['username']):
                raise forms.ValidationError(
                    _('Usernames can only contain letters, numbers and underscores and cannot begin with number.'))
            if len(self.cleaned_data['username']) < 4:
                raise forms.ValidationError(_('Username can\'t be shorter than 4 characters.'))
            if len(self.cleaned_data['username']) > 20:
                raise forms.ValidationError(_('Username can\'t be longer than 20 characters.'))
            try:
                user = User.objects.get(username__exact=self.cleaned_data['username'])
            except User.DoesNotExist:
                return self.cleaned_data['username']
            raise forms.ValidationError(_('This username is already taken. Please choose another.'))

    def clean_email(self):
        """
        Validates that the email is not already	in use.
        """
        if 'email' in self.cleaned_data:
            try:
                email = User.objects.get(email__exact=self.cleaned_data['email'])
            except User.DoesNotExist:
                return self.cleaned_data['email']
            except:
                raise forms.ValidationError(
                    _('Someone else registered with this email address. Please choose another.'))
            raise forms.ValidationError(_('Someone else registered with this email address. Please choose another.'))

    def clean_password2(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data and self.cleaned_data['password1'] == \
                self.cleaned_data['password2']:
            return self.cleaned_data['password2']
        raise forms.ValidationError(_('You must type the same password each time'))


class RegistrationShortForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput)

    def clean_username(self):
        """
        Validates that the username is alphanumeric and is not already
        in use.
        """
        username_re = re.compile(r'^[A-Za-z]{1,}\w*$')

        if 'username' in self.cleaned_data:
            if not username_re.search(self.cleaned_data['username']):
                raise forms.ValidationError(
                    _('Usernames can only contain letters, numbers and underscores and cannot begin with number.'))
            if len(self.cleaned_data['username']) < 4:
                raise forms.ValidationError(_('Username can\'t be shorter than 4 characters.'))
            if len(self.cleaned_data['username']) > 20:
                raise forms.ValidationError(_('Username can\'t be longer than 20 characters.'))
            try:
                user = User.objects.get(username__exact=self.cleaned_data['username'])
            except User.DoesNotExist:
                return self.cleaned_data['username']
            raise forms.ValidationError(_('This username is already taken. Please choose another.'))
