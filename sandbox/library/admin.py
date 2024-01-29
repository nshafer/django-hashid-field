from django.contrib import admin

from library.models import Author, Editor, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'int_id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)

    def int_id(self, obj):
        return obj.id.id


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'reference_id', 'int_reference_id', 'key', 'alt', 'author')
    list_select_related = ('author',)
    list_filter = ('author__name',)
    search_fields = ('name', 'reference_id')
    ordering = ('reference_id', 'id')

    def int_reference_id(self, obj):
        return obj.reference_id.id
