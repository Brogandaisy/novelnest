from django.shortcuts import render

# Create your views here.

# Book List - This displays the list of books - User must be logged in 
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(added_by=self.request.user)

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
