from django.db import models

from hashid_field import HashidField, BigHashidField, HashidAutoField, BigHashidAutoField


class Artist(models.Model):
    id = BigHashidAutoField(primary_key=True, min_length=20)
    name = models.CharField(max_length=40)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)


class Record(models.Model):
    id = HashidAutoField(primary_key=True)
    name = models.CharField(max_length=40)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name="records")
    reference_id = HashidField()
    prefixed_id = HashidField(null=True, blank=True, prefix="prefix_")
    string_id = HashidField(null=True, blank=True, enable_hashid_object=False)
    plain_hashid = HashidField(null=True, blank=True, enable_descriptor=False)
    plain_id = HashidField(null=True, blank=True, enable_descriptor=False, enable_hashid_object=False)
    alternate_id = HashidField(salt="a different salt", null=True, blank=True)
    key = BigHashidField(min_length=10, alphabet="abcdlmnotuvwxyz123789", null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.reference_id)


class Track(models.Model):
    id = BigHashidAutoField(primary_key=True, allow_int_lookup=True, min_length=10, prefix='albumtrack:', salt="abcd", alphabet="abcdefghijklmnop")


class RecordLabel(models.Model):
    def name_prefix(model_class, **kw):
        return model_class._meta.verbose_name.replace(' ', '_') + '/'

    id = HashidAutoField(primary_key=True, allow_int_lookup=True, prefix=name_prefix)
