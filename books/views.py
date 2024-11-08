from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


# Create your views here.

# Book List - This displays the list of books - User must be logged in 
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
            # Allowing Admins can see all books
        else:
            return Book.objects.filter(added_by=self.request.user)
            # Non-Admins can only see their books

# Detailed Book View - This shows further details of the book
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'

# Creating a new book to the users list of books - User must be logged in to add a book
class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['title', 'author', 'status']

    def form_valid(self, form):
        form.instance.added_by = self.request.user  # Connects the user to the book
        return super().form_valid(form)

# Updating a book. Allowing user to edit book details - User must be logged in
class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['title', 'author', 'status']

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.added_by or self.request.user.is_superuser

# Allowing users to delete the book that they have uploaded - user must be logg in
class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.added_by or self.request.user.is_superuser

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after signup
            return redirect('book_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})