from django.conf.urls import url
from django.views import generic

from library import views

app_name = "library"
urlpatterns = [
    url(r'^$', generic.TemplateView.as_view(template_name="library/index.html"), name="index"),
    url(r'^authors$', views.AuthorListView.as_view(), name="authors"),
    url(r'^author/(?P<pk>[0-9a-zA-Z]+)/$', views.AuthorDetailView.as_view(), name="author-detail"),
    url(r'^books$', views.BookListView.as_view(), name="books"),
    url(r'^book/(?P<pk>[0-9a-zA-Z]+)/$', views.BookDetailView.as_view(), name="book-detail"),
]
