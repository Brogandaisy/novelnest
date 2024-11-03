from django.shortcuts import render

# Create your views here.

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(added_by=self.request.user)

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
