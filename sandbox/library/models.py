from django.core.urlresolvers import reverse
from django.db import models

from hashid_field import HashidAutoField, HashidField


class Author(models.Model):
    id = HashidAutoField(primary_key=True)
    name = models.CharField(max_length=40)
    uid = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.name


class Editor(models.Model):
    id = HashidAutoField(primary_key=True, salt="A different salt", min_length=20)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=40)
    author = models.ForeignKey(Author, null=True, blank=True, related_name='books')
    reference_id = HashidField(salt="alternative salt", allow_int=True)
    key = HashidField(min_length=10, alphabet="abcdlmnotuvwxyz0123789", null=True, blank=True)
    some_number = models.IntegerField(null=True, blank=True)
    editors = models.ManyToManyField(Editor, blank=True)

    def get_absolute_url(self):
        return reverse("library:book-detail", kwargs={'pk': self.pk})

    def __str__(self):
        return "{} ({})".format(self.name, self.reference_id)
