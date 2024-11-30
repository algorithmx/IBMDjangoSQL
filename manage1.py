#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import json
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand, CommandError
from onlinecourse.models import Course, Question, Choice
from django.conf import settings

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Check if the command is to load data from JSON
    if len(sys.argv) > 1 and sys.argv[1] == 'load_data':
        if len(sys.argv) < 3:
            print("Please provide the path to the JSON file.")
            sys.exit(1)
        
        json_file_path = sys.argv[2]
        load_data_from_json(json_file_path)
    else:
        execute_from_command_line(sys.argv)

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    for course_data in data.get('courses', []):
        course, created = Course.objects.get_or_create(
            name=course_data['name'],
            defaults={
                'description': course_data.get('description', ''),
                'pub_date': course_data.get('pub_date', None),
                'total_enrollment': course_data.get('total_enrollment', 0)
            }
        )
        if created:
            print(f"Created course: {course.name}")
        
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

if __name__ == '__main__':
    main()
