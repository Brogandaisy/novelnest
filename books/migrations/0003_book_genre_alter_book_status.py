# Generated by Django 5.1.2 on 2024-11-11 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0002_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="genre",
            field=models.CharField(
                choices=[
                    ("fiction", "Fiction"),
                    ("nonfiction", "Non-Fiction"),
                    ("fantasy", "Fantasy"),
                    ("mystery", "Mystery"),
                    ("science_fiction", "Science Fiction"),
                    ("biography", "Biography"),
                    ("history", "History"),
                    ("self_help", "Self Help"),
                    ("romance", "Romance"),
                ],
                default="fiction",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="status",
            field=models.CharField(
                choices=[
                    ("wishlist", "Wish List"),
                    ("Reading", "Reading"),
                    ("Completed", "Completed"),
                ],
                default="to_read",
                max_length=10,
            ),
        ),
    ]
