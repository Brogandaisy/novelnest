from django.urls import path
from . import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="book_list"),  # List all books
    path("add/", views.BookCreateView.as_view(), name="book_add"),  # Add a new book
    path("<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),  # View book details
    path("<int:pk>/edit/", views.BookUpdateView.as_view(), name="book_edit"),  # Edit a book
    path("<int:pk>/delete/", views.BookDeleteView.as_view(), name="book_delete"),  # Delete a book
    path("search/", views.BookSearchView.as_view(), name="book_search"),  # Book search
]
