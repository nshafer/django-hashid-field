from django import forms
from django.core import exceptions
from django.test import TestCase

from hashid_field import Hashid
from library.models import Book, Author


class HashidTests(TestCase):
    def test_integer(self):
        h = Hashid(5)
        self.assertIsInstance(h, Hashid)
        self.assertEqual(h.id, 5)
        self.assertEqual(h.hashid, h.hashids.encode(5))

    def test_hashid(self):
        h = Hashid(123)
        b = Hashid(h.hashid)
        self.assertEqual(h, b)
        self.assertEqual(h.id, b.id)
        self.assertEqual(h.hashid, b.hashid)

    def test_negative_integer(self):
        with self.assertRaises(Exception):
            h = Hashid(-5)

    def test_invalid_hashid(self):
        with self.assertRaises(Exception):
            h = Hashid('asdfqwer')

    def test_min_length(self):
        h = Hashid(456, min_length=10)
        self.assertEqual(len(h.hashid), 10)
        self.assertEqual(len(h), 10)

    def test_hashable(self):
        h = Hashid(987)
        d = {h: "some value"}
        self.assertEqual(d[h], "some value")


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('name', 'reference_id')


class BookTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(name="Test Book", reference_id=123, key=456)
        self.hashids = self.book.reference_id.hashids

    def test_book_create(self):
        self.assertIsInstance(self.book, Book)

    def test_book_reference_is_hashid(self):
        self.assertIsInstance(self.book.reference_id, Hashid)
        self.assertEqual(str(self.book.reference_id), self.hashids.encode(123))

    def test_book_load_from_db(self):
        book = Book.objects.get(pk=self.book.pk)
        self.assertIsInstance(book, Book)

    def test_book_reference_from_db_is_hashid(self):
        book = Book.objects.get(pk=self.book.pk)
        self.assertIsInstance(self.book.reference_id, Hashid)
        self.assertEqual(book.reference_id.hashid, self.hashids.encode(123))

    def test_set_int(self):
        self.book.reference_id = 456
        self.book.save()
        self.assertEqual(self.book.reference_id.hashid, self.hashids.encode(456))

    def test_set_hashid(self):
        self.book.reference_id = self.hashids.encode(789)
        self.book.save()
        self.assertEqual(str(self.book.reference_id), self.hashids.encode(789))

    def test_filter_by_int(self):
        self.assertTrue(Book.objects.filter(reference_id=123).exists())

    def test_filter_by_hashid(self):
        self.assertTrue(Book.objects.filter(reference_id=self.hashids.encode(123)).exists())

    def test_invalid_int(self):
        with self.assertRaises(ValueError):
            self.book.reference_id = -5
            self.book.save()

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            self.book.reference_id = "asdfqwer"
            self.book.save()

    def test_min_length(self):
        self.assertGreaterEqual(len(self.book.key), 10)

    def test_alphabet(self):
        for char in "efghijkpqrs4560":
            self.assertNotIn(char, self.book.key.hashid)

    def test_book_form(self):
        form = BookForm(instance=self.book)
        self.assertEqual(form.initial['reference_id'].hashid, self.hashids.encode(123))
        form = BookForm({'name': "A new name", 'reference_id': 987}, instance=self.book)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(self.book, instance)
        self.assertEqual(str(self.book.reference_id), self.hashids.encode(987))

    def test_invalid_id_in_form(self):
        form = BookForm({'name': "A new name", 'reference_id': "asdfqwer"})
        self.assertFalse(form.is_valid())


class AuthorTests(TestCase):
    def test_autofield(self):
        a = Author.objects.create(name="John Doe")
        b = Author.objects.create(name="Jane Doe")
        a.refresh_from_db()
        b.refresh_from_db()
        self.assertIsInstance(a.id, Hashid)
        self.assertIsInstance(b.id, Hashid)
        self.assertListEqual(list(Author.objects.order_by('id')), [a, b])
