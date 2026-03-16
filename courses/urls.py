from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:pk>/enroll/', views.enroll, name='enroll'),
    path('course/<int:pk>/lessons/', views.lesson_list, name='lesson_list'),
    path('course/<int:course_pk>/lesson/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    path('course/<int:pk>/review/', views.add_review, name='add_review'),
    path('course/<int:pk>/certificate/', views.certificate, name='certificate'),
    path('course/<int:course_pk>/quiz/', views.quiz_view, name='quiz'),
    path('course/<int:course_pk>/forum/', views.forum, name='forum'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('achievements/', views.achievements, name='achievements'),
path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]