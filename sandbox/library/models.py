from django.db import models
from hashid_field.field import HashidCharField

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
    char_id = HashidCharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=40)
    author = models.ForeignKey(Author, null=True, blank=True, related_name='books')
    reference_id = HashidField(salt="alternative salt")
    key = HashidField(min_length=10, alphabet="abcdlmnotuvwxyz0123789", null=True, blank=True)
    some_number = models.IntegerField(null=True, blank=True)
    editors = models.ManyToManyField(Editor, blank=True)

    def save(self, *args, **kwargs):
        super(Book, self).save(*args, **kwargs)
        if self.id and not self.char_id:
            self.char_id = self.id
            super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self.name, self.reference_id)
