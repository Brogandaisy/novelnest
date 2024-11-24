# NovelNest - Book Tracking App
Project 4 - Brogan Carpenter

[View Live Project](https://taylorswift-erastour-0edb3552fd4f.herokuapp.com/)

1. [About the Project](#about-the-project)
2. [Features](#features)
3. [Testing](#testing)
4. [Bugs](#bugs)
5. [Validator Testing](#validator-testing)
6. [Deployment](#deployment)
7. [References](#references)

# About the Project

NovelNest is a website for book lovers who want to keep track of their reading. It’s designed to make organising your books easy, whether it’s ones you want to read, are currently reading, or have already finished. You can also add your own reviews and update them as you go.

## What it does

### Organises your books: 
Add books to lists like “Wish List,” “Currently Reading,” or “Completed” so you can stay on top of your progress.

### Leave reviews: 
Write reviews for the books you’ve read.
### Manage everything easily: 
Quickly move books between lists, update details, and keep everything neat and tidy.
### Clean, user-friendly design:
The site is easy to use and looks good on both desktop and mobile.

## Why use NovelNest?
NovelNest is built to make life easier for readers. It’s not just about tracking books – it’s about enjoying the process of reading, reflecting on what you’ve read, and keeping your library organised. Whether you’re tackling a massive to-read pile or keeping track of favourites, NovelNest is your go-to tool.

# Features

## Create an account with a username and password
Users can register on the platform using Django's built-in authentication system. The form is styled with Bootstrap classes for a clean, user-friendly design.

![Create an Account](static/assets/images/readMe/createaccountnovelnest.png)

## Login and Logout
Users can log in and log out securely using Django’s built-in authentication system. The dynamic login/logout button in the Bootstrap navbar updates based on the user’s session state. 

{% if user.is_authenticated %}

## Change Password
The password change feature uses Django’s built-in PasswordChangeView, which allows users to securely update their passwords. I’ve customised this functionality by creating a CustomPasswordChangeView that uses a personalised form template (password_change_form.html) and a confirmation page (password_change_done.html). Both templates extend base.html to match the styling and layout of the rest of the website, providing a consistent and user-friendly experience for anyone updating their password.

          class CustomPasswordChangeView(PasswordChangeView):
              template_name = "registration/password_change_form.html"  # Ensure this file exists
              success_url = reverse_lazy('password-change/done')  # Matches the name in your URLs

## Upload a book with details (author, title, and genre)
Users can submit book details via a Django form, including author, genre and title, which validates input and saves the data to the database. Bootstrap is used for form styling to ensure responsive layout.



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

![Upload a Book](static/assets/images/readMe/addabooknovelnest.png)

## Select a category for the book (Wish List, Currently Reading, Completed)
A dropdown menu, created with HTML and styled using Bootstrap, lets users assign books to categories. The selection updates dynamically in the database.

![Select a Category](static/assets/images/readMe/selectacategorynovelnest.png)

## Edit, amend or delete uploaded books, and move them between categories
Users can edit book details using Django's update view, with form fields pre-populated from the database. When deleting a book from the users lists, an alert page is displayed to confirm deletion. The webpage redirects to the book detail page once saved, or deleted.

The edit and delete buttons only display if the logged in user has uploaded the book they are viewing.

      {% if user.is_authenticated and book.added_by == user %}

![Edit and Delete](static/assets/images/readMe/editnovelnest.png)

## Book list page with a count of books in each category
A Django query creates book counts by category and puts them dynamically in the template. 

    from django.db.models import Count
    
    context["wish_list_count"] = context["wish_list_books"].count()
        context["reading_count"] = context["reading_books"].count()
        context["completed_count"] = context["completed_books"].count()

The feature counts how many books are in each category (Wish List, Currently Reading, and Completed) using Django’s .count() method. These totals are sent to the template to show users a summary of their books.

The page layout uses a Bootstrap grid to display book lists and category counts clearly.

## Search bar function to search books by author or title
The search feature uses Django ORM to query the database for books based on user input, with results displayed in real-time. 

The BookSearchView class uses get_queryset to find books by title or author based on a search term (q) from the URL. If no search term is provided, it shows no results.

    class BookSearchView(ListView):
        model = Book
        template_name = "books/book_search.html"
        context_object_name = "search_results"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query: 
            return Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
        return Book.objects.none()

## View book details (author, title, and reviews)
Individual book pages dynamically pull data using Django views. It also includes the books reviews, and shows a review form to write a review but only to logged-in users who meet certain conditions (e.g., the book they have uploaded is marked as "Completed" or they search a book which wasn't uploaded by them). 

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

If the user views a book which they did not upload to their account, they can leave a review but have to tick a tickbox confirming they have 'read the book'. This way, reviews stay for users who have read the book and they are trusted for other users.

        if self.object.added_by != request.user:
            has_read = request.POST.get("has_read")
            if not has_read:
                messages.error(request, "You must confirm you have read the book before leaving a review.")
                return redirect(self.object.get_absolute_url())

## Dynamic data: Recently uploaded books and most-reviewed books
The homepage uses Django queries to pull data dynamically, showing the 6 most recent books and 3 most-reviewed books. These are displayed using Bootstrap card decks for a visually engaging layout. This feature has been used on various other pages, where I would like to display other books for users to see. These will change when more books are being uploaded to the database.

          def homepage(request):
    recent_books = Book.objects.order_by('-id')[:6]  # Get the 6 most recent books
    most_reviewed_books = Book.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:3]  # Get the 3 most reviewed books
    return render(request, 'books/homepage.html', {
        'recent_books': recent_books,
        'most_reviewed_books': most_reviewed_books,
    })

## Logged in vs Logged Out Views - LoginRequiredMixin
The LoginRequiredMixin is used throughout the class base views within books/views.py to restrict access to certain views, like the book list, ensuring only logged-in users can view them, while other views, like the book detail view, are accessible to everyone but display additional content or functionality for logged-in users.

Logged In Content:
     
     class BookListView(LoginRequiredMixin, ListView):
         model = Book
         template_name = "books/book_list.html"

Logged Out Content:
     
     class BookDetailView(DetailView):
         model = Book
         template_name = "books/book_detail.html"


# Testing
To test the functionality of the program I used the following systems:

- pep8ci.herokuapp.com / Which checks for any errors in my python code
- Heroku / App deployment, testing the user experience

Testing included typing in the correct requirements for each question multiple times to show it provides the right data each time, but equally testing incorrect data entry, for example: using a number which was not listed. See image below, when answering the album list with '0' it returned an error message, which shows the code is working.

I also tried using incorrect formats such as string/words which displayed the correct error message also.

When testing on pep8, the errors returned were line character maximums and function spacing errors. This was updated and tested again.

<table>
  <thead>
    <tr>
      <th>Function Test</th>
      <th>Test Response</th>
      <th>Test Reaction/Fix</th>
     
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Google Sheet Connection</td>
      <td>After printing the data frames to the terminal the response returned 'Unable to locate file name taylorswift_erastour'</td>
      <td>Ensured the creds.json file was updated and the google sheet had authroised access to edit. (Adding the client email taylorswift-erastour@macro-virtue-429510-d5.iam.gserviceaccount.com)</td>
    </tr>
    <tr>
       <td>Question Number System</td>
       <td>After checking different numbers into the user input box, I can check the error messages displayed. When using numbers 1-6, the functions returned the answers correctly, but when using a number outside of this range, an error message returned. On one occasion, when entering '5' the function was not called, and data answers were produced and no error message were displayed.</td>
      <td>When checking the function for question 5, it was the 'favourite song' function, when going back into the code i realised there had been some spacing issues which resulted in the function not being called. Once this was fixed, i ran the test of question 5 again, where it displayed the favourite song.</td>
    </tr>
    <tr>
      <td>Deployment Tests</td>
      <td>When deploying the code to the app platform heroku, it kept providing an error message of not locating the creds.json file, or gspread.</td>
      <td>I went in and tested each option, checking the creds.json file, the settings on heroku, and noticed the additional config var was not added, and the programs and code libraries were not all installed. Once installed, and config var was added, the file was called without issue.</td>
    </tr>
    <tr>
    <td>Testing User Messaging</td>
    <td>When first writing my code and doing the first test, I noticed the text displayed to the user was in an incorrect order. This meant understanding where to put the user input was confusing.</td></td>
    <td>I adjusted the order of the print text and when they were called within my python code to amend the order the user read the text. I also added line breaks, to make it even clearer when using the while loop and getting the data answers.</td>
 
  </tbody>
</table>


![Testing](https://github.com/Brogandaisy/tayorswift_erastour/blob/main/assets/images/ts_app_display5.png)

# Bugs
During the development, testing, and deployment of the project, I encountered a range of bugs that required careful troubleshooting and debugging. Here’s a summary of some of the key issues:

- Syntax Errors: Common mistakes like capital letters, incorrect indents, misspellings, misplaced commas, and other minor syntax issues in Django views, models, and Bootstrap styling caused disruptions.
- File Tree Problems: Authorisation folders were placed in the wrong directories, and there were duplicate templates/registration folders. The file structure was reorganised, and settings.py was updated for static files, including fixing STATIC_ROOT = BASE_DIR / 'staticfiles'.
- Templates Not Rendering: Templates failed to load due to an incorrectly configured static root, which was corrected to ensure templates pulled through as intended.
- Deployment Bugs: Issues included missing whitenoise from the requirements.txt file and an incorrect database URL, both of which required updates to the configuration.
- Review Functionality: The review feature wasn’t distinguishing between logged-in and logged-out users. Trial and error with Class-Based Views (CBVs) was used to refine the logic so the feature behaved as intended.
- Search Bar Issues: The search bar stopped functioning because it wasn’t pulling books from the database. The issue was traced back to using an incorrect query parameter, which was fixed by changing the parameter to q.
- Port 8000 Not Working: The application wouldn’t run on port 8000 without starting PostgreSQL first. The issue was resolved by ensuring docker start novelnest-postgres was executed before running the server.
- Features Not Working: When logged in and searching for books, the "edit/delete" functionality stopped working because the conditions in views.py were not correctly implemented or were not being properly passed to the template context. This issue was resolved by reviewing and scaling back the styling, ensuring template inheritance was correctly structured, and verifying that all necessary imports and Django functions were included in the appropriate views, templates, and folders.
  
I continuously checked for bugs by running the server with python manage.py runserver 0.0.0.0:8000 and testing functionality such as creating new users, logging in and out, viewing, adding, and deleting books, and changing passwords. Each function was tested thoroughly during development and whenever I updated styling or layouts to ensure everything worked as expected.

A recurring issue I faced was features breaking due to missing or incorrect imports of Django functions in views, templates, or other files. To address this, I now thoroughly check that all necessary imports and dependencies are correctly included in the appropriate places during development.

# Validator Testing

PEP8 Test Returns Clear.

![Pep8 test clear](https://github.com/Brogandaisy/tayorswift_erastour/blob/main/assets/images/pep8.errorclear.png)

# Deployment
This project was deployed using Heroku. My code had been written using gitpod, and committed to github. I used the template repository from Code Institute.

I followed the steps below to create the app display on Heroku:

- Create new app, enter name and country
- Connect to Github account and choose the correct repository
- Select auto deployments, or choose to manually pull (auto ensures it pulls your most up to date commits from github)
- Go to settings and adjust the following:
- Add in your creds.json file as a config var, copy and paste from gitpod, and enter in the box (As this file is hidden from your public github repository)
- Add in the additional config var, (port/8000)
- Install the following buildpacks:
- python and nodejs (ensure they are downloaded in this order)

Once you have this connected, and you have commited your latest edits to github, press 'Open App' at the top of the page and it will display your running program. Here you can test further the user experience.
![Heroku App Deployment](https://github.com/Brogandaisy/tayorswift_erastour/blob/main/assets/images/ts_heroku.png)

# References
I used the following resources to complete this project.

- W3Schools for pandas library explanation, and how to include an enumerate function, and how to round the age to the nearest whole number
- Love Sandwiches walk through project for deployment, and googlesheet import/connection

Author - Brogan Carpenter
