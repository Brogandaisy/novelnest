from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    status_choices = [
        ("Wishlist", "Wish List"),
        ("Reading", "Reading"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default="to_read")
    
    genre_choices = [
        ("fiction", "Fiction"),
        ("nonfiction", "Non-Fiction"),
        ("fantasy", "Fantasy"),
        ("mystery", "Mystery"),
        ("science_fiction", "Science Fiction"),
        ("biography", "Biography"),
        ("history", "History"),
        ("self_help", "Self Help"),
        ("romance", "Romance"),
    ]
    genre = models.CharField(max_length=20, choices=genre_choices, default="fiction")
    
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={"pk": self.pk})


class Review(models.Model):
    content = models.TextField()
    book = models.ForeignKey(Book, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} on {self.book}"
