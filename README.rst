Django Hashids Field
====================

A custom Model Field that uses the `Hashids <http://hashids.org/>`_ library
to obfuscate an IntegerField or AutoField. It can be used in new models or
dropped in place of an existing IntegerField, explicit AutoField, or an
automatically generated AutoField in a model that defines no PrimaryKey.

Installation
------------

Install the package (preferably in a virtualenv):

.. code-block:: bash
    $ pip install django-hashids-field


Basic Usage
-----------

Add it to your model

.. code-block:: python
    from hashids_field import HashidField

    class MyModel(models.Model):
        reference_id = HashidField()

Migrate your database

.. code-block:: bash
    $ ./manage.py makemigrations
    $ ./manage.py migrate



