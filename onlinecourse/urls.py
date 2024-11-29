from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL
    path(route='', view=views.CourseListView.as_view(), name='index'),

    path('registration/', views.registration_request, name='registration'),

    path('login/', views.login_request, name='login'),

    path('logout/', views.logout_request, name='logout'),

    # ex: /onlinecourse/5/
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'), 

    # ex: /onlinecourse/5/lesson/1/
    path('<int:pk>/lesson/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_details'),

    # ex: /onlinecourse/5/enroll/
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # ex: /onlinecourse/5/unenroll/
    path('<int:course_id>/unenroll/', views.unenroll, name='unenroll'),

    # <HINT> Create a route for submit view
    path('<int:course_id>/submit/', views.submit_exam, name='submit'),

    # <HINT> Create a route for show_exam_result view
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name="exam_result"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
