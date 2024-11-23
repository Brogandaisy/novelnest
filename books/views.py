from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Book
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import ReviewForm
from .forms import SearchForm, ReviewForm
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import TemplateView




# Create your views here.

def homepage(request):
    recent_books = Book.objects.order_by('-id')[:6]  # Get the 6 most recent books
    most_reviewed_books = Book.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:3]  # Get the 3 most reviewed books
    return render(request, 'books/homepage.html', {
        'recent_books': recent_books,
        'most_reviewed_books': most_reviewed_books,
    })



# Book List - This displays the list of books - User must be logged in
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "books/book_list.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
            # Allowing Admins can see all books
        else:
            return Book.objects.filter(added_by=self.request.user)
            # Non-Admins can only see their books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = self.get_queryset()

        # Categorise books
        context["wish_list_books"] = books.filter(status="Wishlist")
        context["reading_books"] = books.filter(status="Reading")
        context["completed_books"] = books.filter(status="Completed")

        # Add book totals for each category
        context["wish_list_count"] = context["wish_list_books"].count()
        context["reading_count"] = context["reading_books"].count()
        context["completed_count"] = context["completed_books"].count()

        return context


# Detailed Book View - This shows further details of the book
from django.utils.timezone import now

class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.reviews.all()  # Fetch all reviews for the book
        
        if self.request.user.is_authenticated:
            # Only show the review form to logged-in users
            if self.object.status == "Completed" or self.object.added_by != self.request.user:
                context["review_form"] = ReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check if the user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect(self.object.get_absolute_url())

        # Check if the book uploader is allowed to leave a review (status must be Completed)
        if self.object.added_by == request.user and self.object.status != "Completed":
            messages.error(request, "You can only leave a review if the book is marked as Completed.")
            return redirect(self.object.get_absolute_url())

        # Check if non-uploaders have ticked the checkbox
        if self.object.added_by != request.user:
            has_read = request.POST.get("has_read")
            if not has_read:
                messages.error(request, "You must confirm you have read the book before leaving a review.")
                return redirect(self.object.get_absolute_url())

        # Handle the review form
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = self.object
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted!")
            return redirect(self.object.get_absolute_url())
        else:
            messages.error(request, "There was an error submitting your review.")
            return self.get(request, *args, **kwargs)





# Creating a new book to the users list of books - User must be logged in to add a book
class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = "books/book_form.html"
    fields = ["title", "author", "genre", "status"]
    success_url = reverse_lazy(
        "book_list"
    )  # Redirects to the book list view/page after adding a book

    def form_valid(self, form):
        form.instance.added_by = self.request.user  # Connects the user to the book
        messages.success(
            self.request, "Book added successfully!"
        )  # Displays book added success message
        return super().form_valid(form)


# Updating a book. Allowing user to edit book details - User must be logged in
class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = "books/book_form.html"
    fields = ["title", "author", "genre", "status"]

    def form_valid(self, form):
        messages.success(
            self.request, "Book updated successfully!"
        )  # Displays upload success message
        return super().form_valid(form)

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.added_by or self.request.user.is_superuser


# Allowing users to delete the book that they have uploaded - user must be logg in
class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("book_list")

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request, "Book deleted successfully!"
        )  # Displays delete success message
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.added_by or self.request.user.is_superuser


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after signup
            return redirect("book_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

#Password change page

class CustomPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change_form.html"  # Ensure this file exists
    success_url = reverse_lazy('password-change/done')  # Matches the name in your URLs

    # Admin-Only View


@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class AdminOnlyView(ListView):
    model = Book
    template_name = "books/admin_books.html"  # Admin-only template

# Book Search

class BookSearchView(ListView):
    model = Book
    template_name = "books/book_search.html"
    context_object_name = "search_results"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query:  # Check if query exists
            return Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
        return Book.objects.none()  # Return empty QuerySet if no query


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        context["search_form"] = SearchForm(self.request.GET or None)
        context["query"] = query  # Pass the query back to the template
        context["recent_books"] = Book.objects.order_by('-id')[:3]
        context["most_reviewed_books"] = Book.objects.annotate(
            review_count=Count("reviews")
        ).order_by("-review_count")[:3]
        return context



def about(request):
    return render(request, 'books/about.html')