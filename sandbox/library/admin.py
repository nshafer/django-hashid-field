from django.contrib import admin

from library.models import Author, Editor, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'int_id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)

    def int_id(self, obj):
        return obj.id.id

    def get_search_results(self, request, queryset, search_term):
        print("get_search_results", request, queryset, search_term)
        return super().get_search_results(request, queryset, search_term)


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'reference_id', 'key', 'author')
    search_fields = ('name', 'reference_id')
    ordering = ('reference_id', 'id')
