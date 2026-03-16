from django.contrib import admin
from .models import (Category, Course, Lesson, Enrollment, Review,
                     Quiz, Question, Answer, QuizResult, ForumPost,
                     Achievement, UserAchievement, Notification)

admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(Review)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizResult)
admin.site.register(ForumPost)
admin.site.register(Achievement)
admin.site.register(UserAchievement)
admin.site.register(Notification)