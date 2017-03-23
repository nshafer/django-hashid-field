from django.contrib import admin

from tests.models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass
