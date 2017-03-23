Django Hashid Field
====================

A custom Model Field that uses the `Hashids <http://hashids.org/>`_ `library <https://pypi.python.org/pypi/hashids/>`_
to obfuscate an IntegerField or AutoField. It can be used in new models or dropped in place of an existing IntegerField,
explicit AutoField, or an automatically generated AutoField.

Features
--------

* Stores IDs as integers in the database
* Allows lookups and filtering by either integer, hashid string or Hashid object
* Can disable integer lookups
* Can be used as sort key
* Can drop-in replace an existing IntegerField (HashidField) or AutoField (HashidAutoField)
* Allows specifying a salt globally
* Supports custom *salt*, *min_length* and *alphabet* settings per field
* Supports Django REST Framework Serializers

Requirements
------------

This module is tested and known to work with:

* Python 2.7, 3.5
* Django 1.8, 1.9, 1.10, 1.11
* Hashids 1.1
* Django REST Framework 3.5

Installation
------------

Install the package (preferably in a virtualenv):

.. code-block:: bash

    $ pip install django-hashid-field

Configure a global SALT for all HashidFields to use by default in your settings.py.

.. code-block:: python

    HASHID_FIELD_SALT = "a long and secure salt value that is not the same as SECRET_KEY"
    # Note: You can generate a secure key with:
    #     from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())

Add it to your model

.. code-block:: python

    from hashid_field import HashidField

    class Book(models.Model):
        reference_id = HashidField()

Migrate your database

.. code-block:: bash

    $ ./manage.py makemigrations
    $ ./manage.py migrate

Upgrading
------------

Please see the `Change Log <https://github.com/nshafer/django-hashid-field/blob/master/CHANGELOG.md>`_

Basic Usage
-----------

Use your field like you would any other, for the most part. You can assign integers:

.. code-block:: python

    >>> b = Book()
    >>> b.reference_id = 123
    >>> b.reference_id
    Hashid(123): OwLxW8D

You can assign valid hashids. It's valid only if it can be decoded into an integer based on your salt:

.. code-block:: python

    >>> b.reference_id = 'r8636LO'
    >>> b.reference_id
    Hashid(456): r8636LO

You can access your field with either integers, hashid strings or Hashid objects:

.. code-block:: python

    >>> Book.objects.filter(reference_id=123)
    <QuerySet [<Book:  (OwLxW8D)>]>
    >>> Book.objects.filter(reference_id='OwLxW8D')
    <QuerySet [<Book:  (OwLxW8D)>]>
    >>> b = Book.objects.get(reference_id='OwLxW8D')
    >>> b
    <Book:  (OwLxW8D)>
    >>> h = b.reference_id
    >>> h
    Hashid(123): OwLxW8D
    >>> Book.objects.filter(reference_id=h)
    <Book:  (OwLxW8D)>

The objects returned from a HashidField are an instance of the class Hashid, and allow basic access to the original
integer or the hashid:

.. code-block:: python

    >>> from hashid_field import Hashid
    >>> h = Hashid(123)
    >>> h.id
    123
    >>> h.hashid
    'Mj3'
    >>> print(h)
    Mj3
    >>> repr(h)
    'Hashid(123): Mj3'

Hashid Auto Field
-----------------

Along with ``HashidField`` there is also a ``HashidAutoField`` that works in the same way, but that auto-increments.

.. code-block:: python

    from hashid_field import HashidAutoField

    class Book(models.Model):
        serial_id = HashidAutoField()

The only difference is that if you don't assign a value to it when you save, it will auto-generate a value from your
database, just as an AutoField would do:

.. code-block:: python

    >>> b = Book()
    >>> b.save()
    >>> b.serial_id
    Hashid(1): AJEM7LK

It can be dropped into an existing model that has an auto-created AutoField (all models do by default) as long as you
give it ``primary_key=True``. So if you have this model:

.. code-block:: python

    class Author(models.Model):
        name = models.CharField(max_length=40)

Then Django has created a field for you called 'id' automatically. We just need to override that by specifying our own
field with *primary_key* set to True.

.. code-block:: python

    class Author(models.Model):
        id = HashidAutoField(primary_key=True)
        name = models.CharField(max_length=40)

And now you can use the 'id' or 'pk' attributes on your model instances:

.. code-block:: python

    >>> a = Author.objects.create(name="John Doe")
    >>> a.id
    Hashid(60): N8VNa8z
    >>> Author.objects.get(pk='N8VNa8z')
    <Author: Author object>

Settings
--------

HASHID_FIELD_SALT
~~~~~~~~~~~~~~~~~

You can optionally set a global Salt to be used by all HashFields and HashidAutoFields in your project, or set the salt
on each individual field. Please note that changing this value will cause all HashidFields to change their values, and
any previously published IDs will become invalid.

:Type:    string
:Default: ""
:Example:
    .. code-block:: python

        HASHID_FIELD_SALT = "a long and secure salt value that is not the same as SECRET_KEY"

HASHID_FIELD_ALLOW_INT
~~~~~~~~~~~~~~~~~~~~~~

Global setting on whether or not to allow lookups or fetches of fields using the underlying integer that's stored in the
database. Enabled by default for backwards-compatibility. You can enable this to prevent users from being to do a
sequential scan of objects by pulling objects by integers (1, 2, 3) instead of Hashid strings ("Ba9p1AG", "7V9gk9Z",
"wro12zm").

:Type:    boolean
:Default: True
:Example:
    .. code-block:: python

        HASHID_FIELD_ALLOW_INT = False


Field Parameters
----------------

Besides the standard field options, there are 3 settings you can tweak that are specific to HashidField and
AutoHashidField.

**Please note** that changing any of these values *will* affect the obfuscation of the integers that are
stored in the database, and will change what are considered "valid" hashids. If you have links or URLs that include
your HashidField values, then they will stop working after changing any of these values. It's highly advised that you
don't change any of these settings once you publish any references to your field.

salt
~~~~

:Type:    string
:Default: settings.HASHID_FIELD_SALT, ""
:Example:
    .. code-block:: python

        reference_id = HashidField(salt="Some salt value")

min_length
~~~~~~~~~~

:Type:     int
:Default:  7
:Note:     This defaults to 7 for the field since the maximum IntegerField value can be encoded in 7 characters with
           the default *alphabet* setting of 62 characters.
:Example:
    .. code-block:: python

        reference_id = HashidField(min_length=15)

alphabet
~~~~~~~~

:Type:    string of characters (16 minimum)
:Default: Hashids.ALPHABET, which is "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
:Example:
    .. code-block:: python

        # Only use numbers and lower-case letters
        reference_id = HashidField(alphabet="0123456789abcdefghijklmnopqrstuvwxyz")

allow_int
~~~~~~~~~

:Type:    boolean
:Default: settings.HASHID_FIELD_ALLOW_INT, True
:Example:
    .. code-block:: python

        reference_id = HashidField(allow_int=False)


Hashid Class
------------

Operations with a HashidField or HashidAutoField return a ``Hashid`` object. This simple class does the heavy lifting of
converting integers and hashid strings back and forth. There shouldn't be any need to instantiate these manually.

Methods
~~~~~~~

\__init__(id, salt='', min_length=0, alphabet=Hashids.ALPHABET):
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:id: **REQUIRED** Integer you wish to *encode*
:salt: Salt to use. **Default**: ''
:min_length: Minimum length of encoded hashid string. **Default**: 0
:alphabet: The characters to use in the encoded hashid string. **Default**: Hashids.ALPHABET

set(id)
^^^^^^^

:id: Integer you with to *encode*

Instance Variables
~~~~~~~~~~~~~~~~~~

id
^^

:type: Int
:value: The *decoded* integer

hashid
^^^^^^

:type: String
:value: The *encoded* hashid string

hashids
^^^^^^^

:type: Hashids()
:value: The instance of the Hashids class that is used to *encode* and *decode*


Django REST Framework Integration
=================================

If you wish to use a HashidField or HashidAutoField with a DRF ModelSerializer, there is one extra step that you must
take. Automatic declaration of any Hashid*Fields will result in an ImproperlyConfigured exception being thrown. You
must explicitly declare them in your Serializer, as there is no way for the generated field to know how to work with
a Hashid*Field, specifically what 'salt', 'min_length' and 'alphabet' to use, and can lead to very difficult errors or
behavior to debug, or in the worst case, corruption of your data. Here is an example:

.. code-block:: python

    from rest_framework import serializers
    from hashid_field.rest import HashidSerializerCharField


    class BookSerializer(serializers.ModelSerializer):
        reference_id = HashidSerializerCharField(source_field='library.Book.reference_id')

        class Meta:
            model = Book
            fields = ('id', 'reference_id')

The ``source_field`` allows the HashidSerializerCharField to copy the 'salt', 'min_length' and 'alphabet' settings from
the given field at ``app_name.model_name.field_name`` so that it can be defined in just one place. Explicit settings are
also possible:

.. code-block:: python

    reference_id = HashidSerializerCharField(salt="a different salt", min_length=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ")

If nothing is given, then the field will use the same global settings as a Hashid*Field. It is very important that the
options for the serializer field matches the model field, or else strange errors or data corruption can occur.

HashidSerializerCharField will serialize the value into a Hashids string, but will deserialize either a Hashids string or
integer and save it into the underlying Hashid*Field properly. There is also a HashidSerializerIntegerField that will
serialize the Hashids into an un-encoded integer as well.

Primary Key Related Fields
--------------------------

Any models that have a ForeignKey to another model that uses a Hashid*Field as its Primary Key will need to explicitly
define how the
`PrimaryKeyRelatedField <http://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield>`_
should serialize and deserialize the resulting value using the ``pk_field`` argument. For the given ``Author`` model defined
above that has an ``id = HashidAutoField(primary_key=True)`` set, your BookSerializer should look like the following.

.. code-block:: python

    from rest_framework import serializers
    from hashid_field.rest import HashidSerializerCharField


    class BookSerializer(serializers.ModelSerializer):
        author = serializers.PrimaryKeyRelatedField(pk_field=HashidSerializerCharField(source_field='library.Author.id'), read_only=True)

        class Meta:
            model = Book
            fields = ('id', 'author')

Make sure you pass the source field to the HashidSerializer*Field so that it can copy the 'salt', 'min_length' and 'alphabet'
as described above.

This example sets ``read_only=True`` but you can explicitly define a ``queryset`` or override ``get_queryset(self)`` to allow
read-write behavior.

For a ManyToManyField, you must also remember to pass ``many=True`` to the ``PrimaryKeyRelatedField``.


HashidSerializerCharField
-------------------------

Serialize a Hashid\*Field to a Hashids string, de-serialize either a valid Hashids string or integer into a
Hashid\*Field.

Parameters
~~~~~~~~~~

source_field
^^^^^^^^^^^^

A 3-field dotted notation of the source field to load matching 'salt', 'min_length' and 'alphabet' settings from. Must
be in the format of "app_name.model_name.field_name". Example: "library.Book.reference_id".

salt, min_length, alphabet
^^^^^^^^^^^^^^^^^^^^^^^^^^

See `Field Parameters`_


HashidSerializerIntegerField
============================

Serialize a Hashid\*Field to an integer, de-serialize either a valid Hashids string or integer into a
Hashid\*Field. See `HashidSerializerCharField`_ for parameters.
