import itertools

import django
from django.db.models.lookups import Lookup

from .hashid import Hashid
from .conf import settings

try:
    from django.core.exceptions import EmptyResultSet
except ImportError:
    # Fallback to location in Django <= 1.10
    from django.db.models.sql.datastructures import EmptyResultSet


def get_id_for_hashid_field(field, value):
    if isinstance(value, Hashid):
        return value.id
    try:
        hashid = field.encode_id(value)
    except ValueError:
        raise ValueError(field.error_messages['invalid'] % {'value': value})
    if not field.allow_int_lookup:
        # Check the given value to see if it's an integer lookup, and disallow it.
        # It is possible for real Hashids to resemble integers, especially if the alphabet == "0123456789", so we
        # can't just check if `int(value)` succeeds.
        # Instead, we'll encode the value with the given Hashid*Field, and if resulting Hashids string
        # doesn't match the given value, then we know that something fishy is going on (an integer lookup)
        if value != hashid.hashid:
            raise ValueError(field.error_messages['invalid_hashid'] % {'value': value})
    return hashid.id


# Most of this code is derived or copied from Django 1.11, django/db/models/lookups.py.
# It has been included here to increase compatibility of this module with Django versions 1.8, 1.9 and 1.10.
# Django is Copyright (c) Django Software Foundation and individual contributors.
# Please see https://github.com/django/django/blob/master/LICENSE
# Upon the release of Django 2.0, and when this module drops support for Django < 1.11, most of this code will be
# removed.

class HashidLookup(Lookup):
    get_db_prep_lookup_value_is_iterable = False

    def get_prep_lookup(self):
        if hasattr(self.rhs, '_prepare'):
            if django.VERSION[0] <= 1 and django.VERSION[1] <= 8:
                return self.rhs._prepare()
            else:
                return self.rhs._prepare(self.lhs.output_field)
        return self.rhs

    def process_rhs(self, compiler, connection):
        value = self.rhs
        # Due to historical reasons there are a couple of different
        # ways to produce sql here. get_compiler is likely a Query
        # instance and as_sql just something with as_sql. Finally the value
        # can of course be just plain Python value.
        if hasattr(value, 'get_compiler'):
            value = value.get_compiler(connection=connection)
        if hasattr(value, 'as_sql'):
            sql, params = compiler.compile(value)
            return '(' + sql + ')', params
        if hasattr(value, '_as_sql'):
            sql, params = value._as_sql(connection=connection)
            return '(' + sql + ')', params
        else:
            return self.get_db_prep_lookup(value, connection)

    def batch_process_rhs(self, compiler, connection, rhs=None):
        if rhs is None:
            rhs = self.rhs
        _, params = self.get_db_prep_lookup(rhs, connection)
        sqls, sqls_params = ['%s'] * len(params), params
        return sqls, sqls_params

    def as_sql(self, compiler, connection):
        lhs_sql, params = self.process_lhs(compiler, connection)
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        params.extend(rhs_params)
        rhs_sql = self.get_rhs_op(connection, rhs_sql)
        return '%s %s' % (lhs_sql, rhs_sql), params

    def get_rhs_op(self, connection, rhs):
        return "= %s" % rhs

    def get_db_prep_lookup(self, value, connection):
        # There are two modes this method can be called in... a single value or an iterable of values (usually a set)
        # For a single value, just try to process it, then return the value, or else throw EmptyResultSet
        # For multiple values, process each one in turn. If any of them are invalid, throw it away. If all are invalid,
        # throw EmptyResultSet
        # For relational fields, use the 'field' attribute of the output_field
        field = getattr(self.lhs.output_field, 'field', self.lhs.output_field)
        if self.get_db_prep_lookup_value_is_iterable:
            lookup_ids = []
            for val in value:
                try:
                    lookup_id = get_id_for_hashid_field(field, val)
                except ValueError:
                    if settings.HASHID_FIELD_LOOKUP_EXCEPTION:
                        raise
                    # Ignore this value
                    pass
                else:
                    lookup_ids.append(lookup_id)
            if len(lookup_ids) == 0:
                raise EmptyResultSet
            return '%s', lookup_ids
        else:
            try:
                lookup_id = get_id_for_hashid_field(field, value)
            except ValueError:
                if settings.HASHID_FIELD_LOOKUP_EXCEPTION:
                    raise
                raise EmptyResultSet
            return '%s', [lookup_id]


class HashidIterableLookup(HashidLookup):
    get_db_prep_lookup_value_is_iterable = True

    def get_prep_lookup(self):
        if django.VERSION[0] <= 1 and django.VERSION[1] <= 8:
            return super(HashidIterableLookup, self).get_prep_lookup()
        prepared_values = []
        if hasattr(self.rhs, '_prepare'):
            # A subquery is like an iterable but its items shouldn't be
            # prepared independently.
            return self.rhs._prepare(self.lhs.output_field)
        for rhs_value in self.rhs:
            if hasattr(rhs_value, 'resolve_expression'):
                # An expression will be handled by the database but can coexist
                # alongside real values.
                pass
            prepared_values.append(rhs_value)
        return prepared_values

    def process_rhs(self, compiler, connection):
        db_rhs = getattr(self.rhs, '_db', None)
        if db_rhs is not None and db_rhs != connection.alias:
            raise ValueError(
                "Subqueries aren't allowed across different databases. Force "
                "the inner query to be evaluated using `list(inner_query)`."
            )

        if self.rhs_is_direct_value():
            try:
                rhs = set(self.rhs)
            except TypeError:  # Unhashable items in self.rhs
                rhs = self.rhs

            if not rhs:
                raise EmptyResultSet

            # rhs should be an iterable; use batch_process_rhs() to
            # prepare/transform those values.
            sqls, sqls_params = self.batch_process_rhs(compiler, connection, rhs)
            placeholder = '(' + ', '.join(sqls) + ')'
            return (placeholder, sqls_params)
        else:
            return super(HashidIterableLookup, self).process_rhs(compiler, connection)

    def resolve_expression_parameter(self, compiler, connection, sql, param):
        params = [param]
        if hasattr(param, 'resolve_expression'):
            param = param.resolve_expression(compiler.query)
        if hasattr(param, 'as_sql'):
            sql, params = param.as_sql(compiler, connection)
        return sql, params

    def batch_process_rhs(self, compiler, connection, rhs=None):
        pre_processed = super(HashidIterableLookup, self).batch_process_rhs(compiler, connection, rhs)
        # The params list may contain expressions which compile to a
        # sql/param pair. Zip them to get sql and param pairs that refer to the
        # same argument and attempt to replace them with the result of
        # compiling the param step.
        sql, params = zip(*(
            self.resolve_expression_parameter(compiler, connection, sql, param)
            for sql, param in zip(*pre_processed)
        ))
        params = itertools.chain.from_iterable(params)
        return sql, tuple(params)

    def get_rhs_op(self, connection, rhs):
        return 'IN %s' % rhs
