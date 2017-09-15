from django.http import Http404
from django.views import generic
from rest_framework import viewsets

from library.models import Author, Book
from library.serializers import AuthorSerializer, BookSerializer


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author


class BookListView(generic.ListView):
    model = Book


class BookDetailView(generic.DetailView):
    model = Book


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
