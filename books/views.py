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

def homepage(request):
    """
    Displays the homepage with recent and most-reviewed books.

    """
    recent_books = Book.objects.order_by('-id')[:6]  # Get the 6 most recent books
    most_reviewed_books = Book.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:3]  # Get the 3 most reviewed books
    return render(request, 'books/homepage.html', {
        'recent_books': recent_books,
        'most_reviewed_books': most_reviewed_books,
    })

def signup(request):
    """
    Create a new account for NovelNest. 

    Create a username and password.
    """

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically logs in the user after signup
            return redirect("book_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


class CustomPasswordChangeView(PasswordChangeView):
    """
    When logged in users can change their password with a custom form.
    """
    template_name = "registration/password_change_form.html" 
    success_url = reverse_lazy('password-change/done') 


@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class AdminOnlyView(ListView):
    """
    Admin view for superusers or staff users. They can view all users and uploaded books.

    Superusers can edit and delete users and books.
    """
    model = Book
    template_name = "books/admin_books.html"

class BookCreateView(LoginRequiredMixin, CreateView):
    """
    Upload a new book to their account.
    User can add information including author, genre and category.
    """
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
        )  
        return super().form_valid(form)

class BookListView(LoginRequiredMixin, ListView):
    """
    This displays the list of books which have been uploaded.
    Will only display for a user logged in.
    If requested when logged out, it will display login page.
    Displays the uploaded books in the chosen categories.
    Uses 'count' to display the total number of books in each category.
    """
    model = Book
    template_name = "books/book_list.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
            
        else:
            return Book.objects.filter(added_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = self.get_queryset()

        context["wish_list_books"] = books.filter(status="Wishlist")
        context["reading_books"] = books.filter(status="Reading")
        context["completed_books"] = books.filter(status="Completed")

        context["wish_list_count"] = context["wish_list_books"].count()
        context["reading_count"] = context["reading_books"].count()
        context["completed_count"] = context["completed_books"].count()

        return context

class BookDetailView(DetailView):
    """
    Displays the uploaded books information, including author, genre and title.
    If the user is logged in they will get the option to edit or delete the book.
    If the user is not logged in, it will not display these options.

    Reviews will display if they have been uploaded. 
    The logged in user will only be able to leave a review of the book IF the book is in 'Completed'
    If a non-logged in user is viewing the book, they can leave a review but do the tick box to say 'they've read the book'
    """
    model = Book
    template_name = "books/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.reviews.all()
        
        if self.request.user.is_authenticated:
            if self.object.status == "Completed" or self.object.added_by != self.request.user:
                context["review_form"] = ReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check if the user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect(self.object.get_absolute_url())

        # Check if the book uploader is allowed to leave a review (status must be 'Completed')
        if self.object.added_by == request.user and self.object.status != "Completed":
            messages.error(request, "You can only leave a review if the book is marked as Completed.")
            return redirect(self.object.get_absolute_url())

        # Check if non-uploaders have ticked the checkbox
        if self.object.added_by != request.user:
            has_read = request.POST.get("has_read")
            if not has_read:
                messages.error(request, "You must confirm you have read the book before leaving a review.")
                return redirect(self.object.get_absolute_url())

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


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Users when logged in can edit their uploaded book, including author, title and genre.
    """
    model = Book
    template_name = "books/book_form.html"
    fields = ["title", "author", "genre", "status"]

    def form_valid(self, form):
        messages.success(
            self.request, "Book updated successfully!"
        ) 
        return super().form_valid(form)

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.added_by or self.request.user.is_superuser

class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Users, when logged in can delete a book they've uploaded.
    """
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("book_list")

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request, "Book deleted successfully!"
        ) 
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.added_by or self.request.user.is_superuser

class BookSearchView(ListView):
    """
    Users, logged in or logged out, can search for books on the database.

    Search authors and titles.
    """
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