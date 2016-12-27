Django Hashid Field
====================

A custom Model Field that uses the `Hashids <http://hashids.org/>`_ `library <https://pypi.python.org/pypi/hashids/>`_
to obfuscate an IntegerField or AutoField. It can be used in new models or dropped in place of an existing IntegerField,
explicit AutoField, or an automatically generated AutoField.

Features
--------

* Stores IDs as integers in the database
* Allows lookups and filtering by either integer, hashid string or Hashid object
* Can be used as sort key
* Can drop-in replace an existing IntegerField (HashidField) or AutoField (HashidAutoField)
* Allows specifying a salt globally
* Supports custom *salt*, *min_length* and *alphabet* settings per field

Installation
------------

Install the package (preferably in a virtualenv):

.. code-block:: bash

    $ pip install django-hashid-field


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

Along with `HashidField` there is also a `HashidAutoField` that works in the same way, but that auto-increments.

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
give it `primary_key=True`. So if you have this model:

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
on each individual field.

:Type:    string
:Default: ""
:Example:
    .. code-block:: python

        HASHID_FIELD_SALT = "a long and secure salt value that is not the same as settings.SECRET_KEY"


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
:Default: settings.HASHID_FIELD_SALT
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
