from django import forms

from .models import TestModel


class CreateForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ['title', 'text']


class UpdateForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ['text']
