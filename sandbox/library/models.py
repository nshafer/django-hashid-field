from django.db import models

from hashids_field import HashidsAutoField, HashidsField


class Book(models.Model):
    name = models.CharField(max_length=40)
    reference_id = HashidsField()
    key = HashidsField(min_length=10, alphabet="abcdlmnotuvwxyz0123789")
    some_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.reference_id)


class Author(models.Model):
    id = HashidsAutoField(primary_key=True, min_length=20)
    name = models.CharField(max_length=40)
