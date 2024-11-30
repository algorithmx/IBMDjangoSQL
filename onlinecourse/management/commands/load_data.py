from django.core.management.base import BaseCommand
from onlinecourse.models import Course, Question, Choice, Lesson
import json
from datetime import datetime

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    for course_data in data.get('courses', []):
        pub_date = course_data.get('pub_date', None) if course_data.get('pub_date')!="Today" else datetime.now()
        course, created = Course.objects.get_or_create(
            name=course_data['name'],
            defaults={
                'description': course_data.get('description', ''),
                'pub_date': pub_date,
                'total_enrollment': course_data.get('total_enrollment', 0)
            }
        )
        if created:
            print(f"Created course: {course.name}")
            if course_data.get('image_path'):
                course.set_image_path(course_data.get('image_path'))

        for question_data in course_data.get('questions', []):
            question, q_created = Question.objects.get_or_create(
                course=course,
                content=question_data['content'],
                grade=question_data.get('grade', 50)
            )
            if q_created:
                print(f"  Added question: {question.content}")
            
            for choice_data in question_data.get('choices', []):
                Choice.objects.create(
                    question=question,
                    content=choice_data['content'],
                    is_correct=choice_data.get('is_correct', False)
                )

        # Add lessons to the course
        for lesson_data in course_data.get('lessons', []):
            lesson, l_created = Lesson.objects.get_or_create(
                title=lesson_data['title'],
                order=lesson_data['order'],
                content=lesson_data['content'],
                course=course
            )
            if l_created:
                print(f"  Added lesson: {lesson.title}")

class Command(BaseCommand):
    help = 'My custom command for the onlinecourse app'

    def add_arguments(self, parser):
        # Optional: Add command line arguments
        parser.add_argument('arg', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        if 'arg' in options:
            self.stdout.write(f"Path provided: {options['arg']}")
            load_data_from_json(options['arg'])
        else:
            self.stderr.write("Please provide the path to the JSON file.")