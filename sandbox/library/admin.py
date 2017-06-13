from django.contrib import admin

from library.models import Author, Editor, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('char_id', 'name', 'id', 'reference_id', 'key', 'author')
    search_fields = ('name', 'reference_id')
    ordering = ('reference_id', 'id')
