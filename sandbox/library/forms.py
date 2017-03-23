from django import forms

from library.models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('name', 'author', 'reference_id', 'key', 'some_number', 'editors')
