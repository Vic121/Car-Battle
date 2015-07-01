from django import forms
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User


class LoginAsForm(forms.Form):
    """
    Sometimes to debug an error you need to login as a specific User.
    This form allows you to log as any user in the system. You can restrict
    the allowed users by passing a User queryset paramter, `qs` when the
    form is instantiated.
    """
    user = forms.ModelChoiceField(User.objects.all())

    def __init__(self, data=None, files=None, request=None, qs=None, *args,
                 **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        super(LoginAsForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request
        if qs is not None:
            self.fields["user"].queryset = qs

    def save(self):
        user = self.cleaned_data["user"]

        # In lieu of a call to authenticate()
        backend = get_backends()[0]
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(self.request, user)

        # message = "Logged in as %s" % self.request.user        
        # self.request.user.message_set.create(message=message)
