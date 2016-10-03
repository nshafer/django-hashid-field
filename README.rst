Django Hashid Field
====================

A custom Model Field that uses the `Hashids <http://hashids.org/>`_ library
to obfuscate an IntegerField or AutoField. It can be used in new models or
dropped in place of an existing IntegerField, explicit AutoField, or an
automatically generated AutoField in a model that defines no PrimaryKey.

Features
--------

* Stores IDs as integers in the database
* Can drop-in replace an existing IntegerField (HashidField) or AutoField (HashidAutoField)
* Uses your settings.SECRET_KEY as the salt for the Hashids library
* Supports custom min_length (7 by default) and alphabet characters

Installation
------------

Install the package (preferably in a virtualenv):

.. code-block:: bash

    $ pip install django-hashid-field


Installation
------------

Add it to your model

.. code-block:: python

    from hashid_field import HashidField

    class Book(models.Model):
        reference_id = HashidField()

Migrate your database

.. code-block:: bash

    $ ./manage.py makemigrations
    $ ./manage.py migrate

Basic Usage
-----------

Use your field like you would any other, for the most part. You can assign integers:

.. code-block:: python

    >>> b = Book()
    >>> b.reference_id = 123
    >>> b.reference_id
    Hashid(123): 2L49bGK

You can assign valid hashids. It's valid only if it can be decoded into an integer based on your salt (SECRET_KEY):

.. code-block:: python

    >>> b.reference_id = 'r8636LO'
    >>> b.reference_id
    Hashid(456): r8636LO

You can access your field with either integers or hashids:

.. code-block:: python

    >>> Book.objects.filter(reference_id=123)
    <QuerySet [<Book:  (2L49bGK)>]>
    >>> Book.objects.filter(reference_id='2L49bGK')
    <QuerySet [<Book:  (2L49bGK)>]>
    >>> Book.objects.get(reference_id='2L49bGK')
    <Book:  (2L49bGK)>

The objects returned from a HashidField are Called Hashid, and allow basic access to the original integer or the hashid:

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

    class Book(models.Model):
        serial_id = HashidAutoField()

The only difference is that if you don't assign a value to it when you save, it will auto-generate a value from your
database, just as an AutoField would do:

.. code-block:: python

    >>> b = Book()
    >>> b.save()
    >>> b.serial_id
    Hashid(1): 0985Y8x

It can be dropped into an existing model that has an auto-created AutoField (all models do by default) as long as you
give it `primary_key=True`. So if you have this model:

.. code-block:: python

    class Author(models.Model):
        name = models.CharField(max_length=40)

Then Django has created a field for you called 'id' automatically. We just need to override that:

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

Besides the standard field options, there are 3 settings you can tweak that are specific to HashidField and
AutoHashidField:

    salt
    ~~~~

    Value: Any string
    Default: settings.SECRET_KEY
    Note: You can change this and since the data is stored as an IntegerField in your database, your data won't need to
          be modified, but any usage of old hashid strings will most likely stop working, such as those in URLs and
          links on the web, so it's not suggested that you change this after you set it. The default should be fine in
          99% of cases.
