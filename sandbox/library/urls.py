from django.urls import path, re_path
from django.views import generic

from library import views

app_name = "library"
urlpatterns = [
    re_path(r'^$', generic.TemplateView.as_view(template_name="library/index.html"), name="index"),
    re_path(r'^authors$', views.AuthorListView.as_view(), name="authors"),
    re_path(r'^author/(?P<pk>a_[0-9a-zA-Z]+)/$', views.AuthorDetailView.as_view(), name="author-detail"),
    re_path(r'^books$', views.BookListView.as_view(), name="books"),
    re_path(r'^book/add/$', views.BookCreateView.as_view(), name="book-create"),
    re_path(r'^book/(?P<pk>[0-9a-zA-Z]+)/edit/$', views.BookUpdateView.as_view(), name="book-update"),
    re_path(r'^book/(?P<pk>[0-9a-zA-Z]+)/$', views.BookDetailView.as_view(), name="book-detail"),
]
