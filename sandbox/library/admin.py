from django.contrib import admin

from library.models import Book, Author


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'reference_id', 'key', 'author')
    search_fields = ('name', 'reference_id')
    ordering = ('reference_id', 'id')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)
