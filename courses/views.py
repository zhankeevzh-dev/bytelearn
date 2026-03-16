from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Enrollment, LessonProgress
from .models import Course, Lesson, Enrollment, LessonProgress, Review
from django.db.models import Q, Avg
from django.contrib import messages
from .models import Course, Lesson, Enrollment, LessonProgress, Review, Quiz, Question, Answer, QuizResult, ForumPost
from .models import (Course, Lesson, Enrollment, LessonProgress, Review,
                     Quiz, Question, Answer, QuizResult, ForumPost,
                     Achievement, UserAchievement, Notification)
def home(request):
    courses = Course.objects.all()
    return render(request, 'home.html', {'courses': courses})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lesson_set.all()
    reviews = Review.objects.filter(course=course).select_related('user')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })

@login_required
def enroll(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        # Хабарландыру жібер
        Notification.objects.create(
            user=request.user,
            message=f'✅ "{course.title}" курсына сәтті жазылдыңыз!'
        )
        # Жетістік тексер
        count = Enrollment.objects.filter(user=request.user).count()
        if count == 1:
            give_achievement(request.user, 'first_course')
        elif count == 5:
            give_achievement(request.user, 'five_courses')
    return redirect('lesson_list', pk=pk)

@login_required
def lesson_list(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_detail', pk=pk)
    lessons = course.lesson_set.all()
    progress = LessonProgress.objects.filter(user=request.user, lesson__course=course)
    completed_ids = progress.filter(completed=True).values_list('lesson_id', flat=True)
    total = lessons.count()
    done = len(completed_ids)
    percent = int((done / total) * 100) if total > 0 else 0
    return render(request, 'lesson_list.html', {
        'course': course,
        'lessons': lessons,
        'completed_ids': completed_ids,
        'percent': percent,
        'done': done,
        'total': total,
    })

@login_required
def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_detail', pk=course_pk)
    lessons = course.lesson_set.all()
    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    if request.method == 'POST':
        progress.completed = True
        progress.save()
        completed_count = LessonProgress.objects.filter(
            user=request.user, completed=True
        ).count()
        if completed_count == 1:
            give_achievement(request.user, 'first_lesson')
        elif completed_count == 10:
            give_achievement(request.user, 'ten_lessons')
        next_lesson = lessons.filter(order__gt=lesson.order).first()
        if next_lesson:
            return redirect('lesson_detail', course_pk=course.pk, lesson_pk=next_lesson.pk)
        return redirect('lesson_list', pk=course.pk)
    return render(request, 'lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'progress': progress,
    })

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'my_courses.html', {'enrollments': enrollments})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# 🔍 Іздеу
def search(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else Course.objects.none()
    return render(request, 'search.html', {'courses': courses, 'query': query})

# ⭐ Пікір қалдыру
@login_required
def add_review(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.update_or_create(
            user=request.user, course=course,
            defaults={'rating': rating, 'comment': comment}
        )
    return redirect('course_detail', pk=pk)

# 👤 Профиль
@login_required
def profile(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    completed = LessonProgress.objects.filter(user=request.user, completed=True).count()
    return render(request, 'profile.html', {
        'enrollments': enrollments,
        'completed': completed,
    })

# 🏆 Сертификат
@login_required
def certificate(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    lessons = course.lesson_set.all()
    completed = LessonProgress.objects.filter(
        user=request.user, lesson__course=course, completed=True
    ).count()
    if completed < lessons.count():
        messages.error(request, 'Барлық сабақтарды аяқта!')
        return redirect('lesson_list', pk=pk)
    return render(request, 'certificate.html', {
        'course': course,
        'user': request.user,
    })

# 📊 Статистика дашборд
@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    total_courses = enrollments.count()
    completed_lessons = LessonProgress.objects.filter(user=request.user, completed=True).count()
    total_lessons = LessonProgress.objects.filter(user=request.user).count()
    quiz_results = QuizResult.objects.filter(user=request.user).order_by('-created_at')[:5]
    percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    return render(request, 'dashboard.html', {
        'total_courses': total_courses,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'percent': percent,
        'quiz_results': quiz_results,
        'enrollments': enrollments,
    })

# 🧪 Тест
@login_required
def quiz_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    quiz = get_object_or_404(Quiz, course=course)
    questions = quiz.question_set.prefetch_related('answer_set').all()
    if request.method == 'POST':
        score = 0
        total = questions.count()
        for question in questions:
            selected = request.POST.get(f'q_{question.id}')
            if selected:
                answer = Answer.objects.filter(id=selected, is_correct=True).first()
                if answer:
                    score += 1
        QuizResult.objects.create(user=request.user, quiz=quiz, score=score, total=total)
        return render(request, 'quiz_result.html', {
            'score': score, 'total': total, 'course': course,
            'percent': int((score / total) * 100) if total > 0 else 0
        })
    return render(request, 'quiz.html', {'quiz': quiz, 'questions': questions, 'course': course})

# 💬 Форум
@login_required
def forum(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_detail', pk=course_pk)
    posts = ForumPost.objects.filter(course=course).select_related('user')
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ForumPost.objects.create(user=request.user, course=course, message=message)
        return redirect('forum', course_pk=course_pk)
    return render(request, 'forum.html', {'course': course, 'posts': posts})

# 🔔 Хабарландыруларды оқылды деп белгіле
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', '/'))

# 🏅 Жетістіктер беті
@login_required
def achievements(request):
    all_achievements = Achievement.objects.all()
    earned = UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True)
    return render(request, 'achievements.html', {
        'all_achievements': all_achievements,
        'earned': earned,
    })

# Жетістік беру функциясы (ішкі)
def give_achievement(user, condition):
    try:
        achievement = Achievement.objects.get(condition=condition)
        obj, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
        if created:
            Notification.objects.create(
                user=user,
                message=f'🏅 Жаңа жетістік: {achievement.icon} {achievement.name}'
            )
    except Achievement.DoesNotExist:
        pass