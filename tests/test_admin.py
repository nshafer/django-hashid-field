from django.contrib.admin import AdminSite
from django.test import TestCase

from tests.admin import RecordAdmin
from tests.models import Record


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


site = AdminSite()
request = MockRequest()
request.user = MockSuperUser()


class HashidAdminTests(TestCase):
    def test_admin_widget_is_text(self):
        admin = RecordAdmin(Record, site)
        form_class = admin.get_form(request)
        form = form_class()
        widget = form.fields['reference_id'].widget
        self.assertEqual(widget.input_type, 'text')
