"""
Django management command to create sample data for testing and development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.accounts.models import School
from apps.content.models import Subject, Chapter, Lesson, LessonMedia
from apps.quizzes.models import Quiz, Question
from apps.progress.models import StudentProgress, LearningStreak
from apps.analytics.models import Analytics
from apps.notifications.models import Notification, NotificationTemplate
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='Number of students to create'
        )
        parser.add_argument(
            '--teachers',
            type=int,
            default=10,
            help='Number of teachers to create'
        )
        parser.add_argument(
            '--parents',
            type=int,
            default=30,
            help='Number of parents to create'
        )
        parser.add_argument(
            '--lessons',
            type=int,
            default=100,
            help='Number of lessons to create'
        )
        parser.add_argument(
            '--quizzes',
            type=int,
            default=50,
            help='Number of quizzes to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Create schools
            schools = self.create_schools()
            
            # Create users
            students = self.create_students(options['students'], schools)
            teachers = self.create_teachers(options['teachers'], schools)
            parents = self.create_parents(options['parents'], students)
            
            # Create content
            subjects = self.create_subjects()
            chapters = self.create_chapters(subjects)
            lessons = self.create_lessons(chapters, options['lessons'])
            
            # Create quizzes
            quizzes = self.create_quizzes(subjects, options['quizzes'])
            self.create_questions(quizzes)
            
            # Create progress data
            self.create_progress_data(students, lessons)
            
            # Create analytics data
            self.create_analytics_data(students, teachers, parents, lessons, quizzes)
            
            # Create notifications
            self.create_notifications(students, teachers, parents)
            
            # Create notification templates
            self.create_notification_templates()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(schools)} schools\n'
                f'- {len(students)} students\n'
                f'- {len(teachers)} teachers\n'
                f'- {len(parents)} parents\n'
                f'- {len(subjects)} subjects\n'
                f'- {len(chapters)} chapters\n'
                f'- {len(lessons)} lessons\n'
                f'- {len(quizzes)} quizzes\n'
            )
        )

    def create_schools(self):
        """Create sample schools"""
        schools_data = [
            {'name': 'Addis Ababa Elementary School', 'city': 'Addis Ababa', 'country': 'Ethiopia'},
            {'name': 'Dire Dawa Primary School', 'city': 'Dire Dawa', 'country': 'Ethiopia'},
            {'name': 'Hawassa Learning Center', 'city': 'Hawassa', 'country': 'Ethiopia'},
            {'name': 'Gondar Education Hub', 'city': 'Gondar', 'country': 'Ethiopia'},
            {'name': 'Bahir Dar School', 'city': 'Bahir Dar', 'country': 'Ethiopia'},
        ]
        
        schools = []
        for data in schools_data:
            school, created = School.objects.get_or_create(
                name=data['name'],
                defaults={
                    'city': data['city'],
                    'country': data['country'],
                    'is_active': True
                }
            )
            schools.append(school)
        
        return schools

    def create_students(self, count, schools):
        """Create sample students"""
        students = []
        first_names = ['Abebe', 'Kebede', 'Tigist', 'Meron', 'Yonas', 'Selam', 'Dawit', 'Marta', 'Elias', 'Hana']
        last_names = ['Tesfaye', 'Gebre', 'Assefa', 'Mengistu', 'Hailu', 'Tadesse', 'Kebede', 'Girma', 'Tadesse', 'Worku']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"student{i+1:03d}"
            email = f"{username}@example.com"
            student_id = f"STU{i+1:04d}"
            pin = f"{random.randint(1000, 9999)}"
            grade_level = random.randint(1, 4)
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'STUDENT',
                    'student_id': student_id,
                    'grade_level': grade_level,
                    'school': random.choice(schools),
                    'is_active': True,
                    'is_verified': True
                }
            )
            
            if created:
                user.set_pin(pin)
                user.save()
            
            students.append(user)
        
        return students

    def create_teachers(self, count, schools):
        """Create sample teachers"""
        teachers = []
        first_names = ['Dr. Alem', 'Prof. Bekele', 'Ms. Genet', 'Mr. Haile', 'Dr. Kidist', 'Ms. Lulit', 'Mr. Mesfin', 'Dr. Nardos']
        last_names = ['Tadesse', 'Gebre', 'Assefa', 'Mengistu', 'Hailu', 'Tadesse', 'Kebede', 'Girma']
        subjects = ['Mathematics', 'English', 'Science', 'Social Studies', 'Amharic', 'Art', 'Music', 'Physical Education']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"teacher{i+1:03d}"
            email = f"{username}@school.edu"
            teacher_id = f"TCH{i+1:04d}"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'TEACHER',
                    'teacher_id': teacher_id,
                    'subject_specialties': random.sample(subjects, random.randint(1, 3)),
                    'school': random.choice(schools),
                    'is_active': True,
                    'is_verified': True
                }
            )
            
            if created:
                user.set_password('teacher123')
                user.save()
            
            teachers.append(user)
        
        return teachers

    def create_parents(self, count, students):
        """Create sample parents"""
        parents = []
        first_names = ['Aster', 'Berhanu', 'Chaltu', 'Desta', 'Eleni', 'Fikru', 'Gebre', 'Hirut']
        last_names = ['Tadesse', 'Gebre', 'Assefa', 'Mengistu', 'Hailu', 'Tadesse', 'Kebede', 'Girma']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"parent{i+1:03d}"
            email = f"{username}@example.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'PARENT',
                    'is_active': True,
                    'is_verified': True
                }
            )
            
            if created:
                user.set_password('parent123')
                user.save()
            
            # Assign children
            children_count = random.randint(1, 3)
            children = random.sample(students, min(children_count, len(students)))
            for child in children:
                child.parent = user
                child.save()
            
            parents.append(user)
        
        return parents

    def create_subjects(self):
        """Create sample subjects"""
        subjects_data = [
            {'name': 'Mathematics', 'description': 'Basic math concepts for elementary students', 'grade_level': 1},
            {'name': 'English Language', 'description': 'English language learning', 'grade_level': 1},
            {'name': 'Science', 'description': 'Introduction to science', 'grade_level': 1},
            {'name': 'Amharic', 'description': 'Amharic language and literature', 'grade_level': 1},
            {'name': 'Mathematics', 'description': 'Advanced math concepts', 'grade_level': 2},
            {'name': 'English Language', 'description': 'Intermediate English', 'grade_level': 2},
            {'name': 'Science', 'description': 'Life and physical sciences', 'grade_level': 2},
            {'name': 'Social Studies', 'description': 'History and geography', 'grade_level': 2},
            {'name': 'Mathematics', 'description': 'Algebra and geometry basics', 'grade_level': 3},
            {'name': 'English Language', 'description': 'Advanced English', 'grade_level': 3},
            {'name': 'Science', 'description': 'Earth and space sciences', 'grade_level': 3},
            {'name': 'Mathematics', 'description': 'Pre-algebra and problem solving', 'grade_level': 4},
            {'name': 'English Language', 'description': 'Literature and composition', 'grade_level': 4},
            {'name': 'Science', 'description': 'Environmental science', 'grade_level': 4},
        ]
        
        subjects = []
        for data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=data['name'],
                grade_level=data['grade_level'],
                defaults={
                    'description': data['description'],
                    'is_active': True,
                    'color_code': f"#{random.randint(0, 0xFFFFFF):06x}",
                    'order_index': random.randint(1, 10)
                }
            )
            subjects.append(subject)
        
        return subjects

    def create_chapters(self, subjects):
        """Create sample chapters"""
        chapters = []
        chapter_titles = [
            'Introduction', 'Basics', 'Fundamentals', 'Advanced Concepts',
            'Practice Exercises', 'Review', 'Assessment', 'Applications'
        ]
        
        for subject in subjects:
            chapter_count = random.randint(3, 8)
            for i in range(chapter_count):
                title = f"{random.choice(chapter_titles)} {i+1}"
                chapter, created = Chapter.objects.get_or_create(
                    title=title,
                    subject=subject,
                    defaults={
                        'description': f"Chapter {i+1} of {subject.name}",
                        'order_index': i + 1,
                        'is_active': True,
                        'estimated_duration': random.randint(30, 120)
                    }
                )
                chapters.append(chapter)
        
        return chapters

    def create_lessons(self, chapters, count):
        """Create sample lessons"""
        lessons = []
        lesson_types = ['SLIDES', 'VIDEO', 'AUDIO', 'READING', 'INTERACTIVE']
        lesson_titles = [
            'Introduction to', 'Understanding', 'Learning about', 'Exploring',
            'Mastering', 'Practicing', 'Reviewing', 'Applying'
        ]
        
        for i in range(count):
            chapter = random.choice(chapters)
            lesson_type = random.choice(lesson_types)
            title = f"{random.choice(lesson_titles)} {chapter.title}"
            
            lesson, created = Lesson.objects.get_or_create(
                title=title,
                chapter=chapter,
                defaults={
                    'content': f"This is a sample lesson about {chapter.title}. It contains educational content for students.",
                    'content_type': lesson_type,
                    'duration': random.randint(5, 60),
                    'order_index': random.randint(1, 10),
                    'is_active': True,
                    'is_premium': random.choice([True, False]),
                    'learning_objectives': [
                        f"Understand {chapter.title}",
                        f"Apply concepts from {chapter.title}",
                        f"Practice {chapter.title} skills"
                    ]
                }
            )
            lessons.append(lesson)
        
        return lessons

    def create_quizzes(self, subjects, count):
        """Create sample quizzes"""
        quizzes = []
        quiz_titles = [
            'Basic Quiz', 'Practice Test', 'Assessment', 'Review Quiz',
            'Chapter Test', 'Unit Exam', 'Final Quiz', 'Quick Check'
        ]
        
        for i in range(count):
            subject = random.choice(subjects)
            title = f"{random.choice(quiz_titles)} - {subject.name}"
            
            quiz, created = Quiz.objects.get_or_create(
                title=title,
                subject=subject,
                defaults={
                    'description': f"A quiz about {subject.name}",
                    'grade_level': subject.grade_level,
                    'time_limit': random.randint(10, 60),
                    'max_attempts': random.randint(1, 5),
                    'passing_score': random.randint(60, 90),
                    'is_active': True,
                    'is_premium': random.choice([True, False]),
                    'instructions': 'Answer all questions carefully. Good luck!'
                }
            )
            quizzes.append(quiz)
        
        return quizzes

    def create_questions(self, quizzes):
        """Create sample questions for quizzes"""
        question_types = ['MULTIPLE_CHOICE', 'TRUE_FALSE', 'FILL_IN_BLANK', 'SHORT_ANSWER']
        
        for quiz in quizzes:
            question_count = random.randint(5, 15)
            for i in range(question_count):
                question_type = random.choice(question_types)
                question_text = f"Sample question {i+1} for {quiz.title}"
                
                if question_type == 'MULTIPLE_CHOICE':
                    options = ['Option A', 'Option B', 'Option C', 'Option D']
                    correct_answer = random.choice(options)
                elif question_type == 'TRUE_FALSE':
                    options = []
                    correct_answer = random.choice(['True', 'False'])
                else:
                    options = []
                    correct_answer = f"Sample answer {i+1}"
                
                Question.objects.get_or_create(
                    quiz=quiz,
                    question_text=question_text,
                    defaults={
                        'question_type': question_type,
                        'options': options,
                        'correct_answer': correct_answer,
                        'explanation': f"This is the explanation for question {i+1}",
                        'points': random.randint(1, 5),
                        'order_index': i + 1,
                        'is_active': True,
                        'difficulty_level': random.randint(1, 5)
                    }
                )

    def create_progress_data(self, students, lessons):
        """Create sample progress data"""
        progress_statuses = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'PAUSED']
        
        for student in lessons[:50]:  # Only create progress for first 50 lessons
            lesson = random.choice(lessons)
            status = random.choice(progress_statuses)
            
            progress, created = StudentProgress.objects.get_or_create(
                student=student,
                lesson=lesson,
                defaults={
                    'status': status,
                    'time_spent': random.randint(0, 3600) if status != 'NOT_STARTED' else 0,
                    'score': random.randint(60, 100) if status == 'COMPLETED' else None,
                    'last_position': random.randint(0, 100) if status == 'IN_PROGRESS' else 0
                }
            )
            
            if created and status == 'COMPLETED':
                progress.completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                progress.save()
            
            if created and status in ['IN_PROGRESS', 'COMPLETED']:
                progress.started_at = timezone.now() - timedelta(days=random.randint(1, 30))
                progress.save()

    def create_analytics_data(self, students, teachers, parents, lessons, quizzes):
        """Create sample analytics data"""
        metric_types = [
            'lesson_access', 'lesson_completion', 'quiz_attempt', 'quiz_completion',
            'time_spent', 'score_achieved', 'login_activity'
        ]
        
        # Create analytics for the last 30 days
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            
            # Student analytics
            for student in students[:20]:  # Only for first 20 students
                for _ in range(random.randint(0, 5)):
                    metric_type = random.choice(metric_types)
                    metric_value = random.randint(1, 100)
                    
                    Analytics.objects.get_or_create(
                        student=student,
                        metric_type=metric_type,
                        date=date,
                        defaults={
                            'metric_value': metric_value,
                            'metadata': {
                                'lesson_id': random.choice(lessons).id if 'lesson' in metric_type else None,
                                'quiz_id': random.choice(quizzes).id if 'quiz' in metric_type else None
                            }
                        }
                    )
            
            # Teacher analytics
            for teacher in teachers[:5]:  # Only for first 5 teachers
                for _ in range(random.randint(0, 3)):
                    Analytics.objects.get_or_create(
                        teacher=teacher,
                        metric_type='lesson_access',
                        date=date,
                        defaults={
                            'metric_value': random.randint(1, 50),
                            'metadata': {'action': 'content_created'}
                        }
                    )

    def create_notifications(self, students, teachers, parents):
        """Create sample notifications"""
        notification_types = [
            'LESSON_COMPLETED', 'QUIZ_RESULT', 'ACHIEVEMENT', 'STREAK_MILESTONE',
            'REMINDER', 'SYSTEM', 'PARENT_UPDATE', 'TEACHER_MESSAGE'
        ]
        
        all_users = list(students[:20]) + list(teachers[:5]) + list(parents[:10])
        
        for user in all_users:
            for _ in range(random.randint(0, 5)):
                notification_type = random.choice(notification_types)
                title = f"Sample {notification_type.replace('_', ' ').title()}"
                message = f"This is a sample {notification_type.lower()} notification for {user.get_full_name()}."
                
                Notification.objects.get_or_create(
                    user=user,
                    title=title,
                    notification_type=notification_type,
                    defaults={
                        'message': message,
                        'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                        'is_read': random.choice([True, False]),
                        'is_sent': random.choice([True, False])
                    }
                )

    def create_notification_templates(self):
        """Create sample notification templates"""
        templates_data = [
            {
                'name': 'Lesson Completed',
                'title_template': 'Great job! You completed {lesson_title}',
                'message_template': 'Congratulations on completing {lesson_title}. Keep up the great work!',
                'notification_type': 'LESSON_COMPLETED',
                'priority': 'MEDIUM'
            },
            {
                'name': 'Quiz Result',
                'title_template': 'Quiz Results: {quiz_title}',
                'message_template': 'You scored {score}% on {quiz_title}. {message}',
                'notification_type': 'QUIZ_RESULT',
                'priority': 'HIGH'
            },
            {
                'name': 'Achievement Unlocked',
                'title_template': 'Achievement Unlocked: {achievement_title}',
                'message_template': 'Congratulations! You earned the {achievement_title} achievement.',
                'notification_type': 'ACHIEVEMENT',
                'priority': 'HIGH'
            },
            {
                'name': 'Learning Reminder',
                'title_template': 'Time to learn!',
                'message_template': 'Don\'t forget to continue your learning journey today.',
                'notification_type': 'REMINDER',
                'priority': 'LOW'
            }
        ]
        
        for data in templates_data:
            NotificationTemplate.objects.get_or_create(
                name=data['name'],
                defaults={
                    'title_template': data['title_template'],
                    'message_template': data['message_template'],
                    'notification_type': data['notification_type'],
                    'priority': data['priority'],
                    'is_active': True,
                    'auto_send': False,
                    'variables': ['lesson_title', 'quiz_title', 'score', 'message', 'achievement_title']
                }
            )
