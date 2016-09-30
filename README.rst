A sample Python project
=======================

A sample project that exists as an aid to the `Python Packaging User Guide
<https://packaging.python.org>`_'s `Tutorial on Packaging and Distributing
Projects <https://packaging.python.org/en/latest/distributing.html>`_.

This projects does not aim to cover best practices for Python project
development as a whole. For example, it does not provide guidance or tool
recommendations for version control, documentation, or testing.

----

This is the README file for the project.

The file should use UTF-8 encoding and be written using ReStructured Text. It
will be used to generate the project webpage on PyPI and will be displayed as
the project homepage on common code-hosting services, and should be written for
that purpose.

Typical contents for this file would include an overview of the project, basic
usage examples, etc. Generally, including the project changelog in here is not
a good idea, although a simple "What's New" section for the most recent version
may be appropriate.


Django Patch
============
To enable Django to call pre_save on our custom field when used as the AutoField PK,
django/db/models/base.py line 911

    def _save_table(
        if not updated:
            if update_pk:
                setattr(self, meta.pk.attname, result)
+               meta.pk.pre_save(self, True)
        return updated
