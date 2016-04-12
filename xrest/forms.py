from django import forms
from django.conf import settings


class LimitOffsetForm(forms.Form):
    offset = forms.IntegerField(min_value=0, initial=settings.XREST_DEFAULT_LIST_LIMIT, required=False)
    limit = forms.IntegerField(min_value=1, initial=1, required=False)
