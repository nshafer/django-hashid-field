from django.db import models

from hashid_field import HashidAutoField, HashidField


class Artist(models.Model):
    id = HashidAutoField(primary_key=True, min_length=20)
    name = models.CharField(max_length=40)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)


class Record(models.Model):
    name = models.CharField(max_length=40)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name="records")
    reference_id = HashidField()
    alternate_id = HashidField(salt="a different salt", null=True, blank=True)
    key = HashidField(min_length=10, alphabet="abcdlmnotuvwxyz123789", null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.reference_id)


class Track(models.Model):
    id = HashidAutoField(primary_key=True, allow_int_lookup=True, min_length=10, prefix='albumtrack:', salt="abcd", alphabet="abcdefghijklmnop")


class RecordLabel(models.Model):
    def name_prefix(model_class, **kw):
        return model_class._meta.verbose_name.replace(' ', '_') + '/'

    id = HashidAutoField(primary_key=True, allow_int_lookup=True, prefix=name_prefix)