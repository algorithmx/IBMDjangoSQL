from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from .models import Course, Enrollment, Submission, Lesson
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


class LessonDetailView(generic.DetailView):
    model = Lesson
    template_name = 'onlinecourse/lesson_detail_bootstrap.html'
    context_object_name = 'lesson'

    def get_object(self):
        # Get the course first to ensure it exists
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        # Now filter the lessons by lesson_id
        return get_object_or_404(Lesson, course=course, id=self.kwargs['lesson_id'])


def enroll(request, course_id):
    # Once a user enrolled a class, an enrollment entry should 
    # be created between the user and course
    # And we could use the enrollment to track information such as exam submissions
    user = request.user
    if user.is_authenticated:
        course = get_object_or_404(Course, pk=course_id)
        is_enrolled = check_if_enrolled(user, course)
        if not is_enrolled:
            # Create an enrollment
            Enrollment.objects.create(user=user, course=course, mode='honor')
            course.total_enrollment += 1
            course.save()
            return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))
        else:
            # redirect to course details page
            return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))
    else:
        return HttpResponse(f"Unauthenticated user")

def unenroll(request, course_id):
    user = request.user
    if user.is_authenticated:
        course = get_object_or_404(Course, pk=course_id)
        is_enrolled = check_if_enrolled(user, course)
        if is_enrolled:
            Enrollment.objects.filter(user=user, course=course).delete()
            course.total_enrollment -= 1
            course.save()
            return HttpResponseRedirect(reverse(viewname='onlinecourse:index', args=()))
        else:
            return HttpResponse(f"User {user.username} is not enrolled in course {course.id}")
    else:
        return HttpResponse(f"Unauthenticated user")


#TODO check
# submit view to create an exam submission record for a course enrollment
def submit_exam(request, course_id):
    # Get user and course object
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    # get the associated enrollment object created when the user enrolled the course
    enrollment = Enrollment.objects.get(user=user, course=course)
    if enrollment is None:
        # return error message
        return HttpResponse(f"You ({user.username}) are not enrolled in this course {course.id}")
    else:
        # Create a submission object referring to the enrollment
        submission = Submission.objects.create(enrollment=enrollment)
        if submission is None:
            return HttpResponse(f"Failed to create submission for enrollment {enrollment.id}")
        else:
            # Collect the selected choices from exam form
            selected_choices = extract_answers(request)
            # Add each selected choice object to the submission object
            submission.choices.set(selected_choices)
            # Redirect to show_exam_result with the submission id
            submission.save()
            return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course.id, submission.id)))


# An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers


# exam result view to check if learner passed exam and show their 
# question results and result for each question,
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()  # Assuming course has related questions

    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)  # Get all correct choices for the question
        selected_choices = choices.filter(question=question)  # Get the user's selected choices for the question

        # Check if the selected choices are the same as the correct choices
        if set(correct_choices) == set(selected_choices):
            total_score += question.grade  # Add the question's grade only if all correct answers are selected

    return render(
        request, 
        'onlinecourse/exam_result_bootstrap.html',
        {
            'course': course,
            'grade': total_score,
            'choices': choices
        }
    )
    