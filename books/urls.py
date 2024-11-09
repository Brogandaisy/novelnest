from django.urls import path
from . import views
from .views import AdminOnlyView


urlpatterns = [
    path("admin-only/", AdminOnlyView.as_view(), name="admin_only"),  # Admin only
    path("", views.BookListView.as_view(), name="book_list"),  # List all books
    path("signup/", views.signup, name="signup"),  # Signup page
    path("add/", views.BookCreateView.as_view(), name="book_add"),  # Add a new book
    path(
        "<int:pk>/", views.BookDetailView.as_view(), name="book_detail"
    ),  # View book details
    path(
        "<int:pk>/edit/", views.BookUpdateView.as_view(), name="book_edit"
    ),  # Edit a book
    path(
        "<int:pk>/delete/", views.BookDeleteView.as_view(), name="book_delete"
    ),  # Delete a book
]
