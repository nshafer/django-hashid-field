from django import forms

from tests.models import Record


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ('name', 'reference_id')


class AlternateRecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ('name', 'reference_id', 'alternate_id')
