Final Project
===

This is my work on the final project for the course []() on Coursera. 

To lauch the project, follow the instructions below:

- clone the repo
- create and activate virtual environment
- install django and other required packages 
- **run the commands below to initialize the project**
  - `python manage.py makemigrations`
  - `python manage.py migrate`
  - `python manage.py runserver`
  - Ctrl+C to stop the server
  - `python manage.py createsuperuser` and add `admin` user
  - `python manage.py load_data static/coursecontent/django_test_course.json`
  - `python manage.py runserver`
- check the main page and the admin page with appropriate URLs