from django.urls import path
from .views import *
urlpatterns = [
    path('', homepage),
    path('company-form/', createCompany, name='company-form'),
    path('student-form/', student_view, name='student-form'),
    path('universities-form/', student_view, name='universities-form'),
    path('teachers-form/', student_view, name='teachers-form'),
    path('events-form/', student_view, name='events-form'),
    path('projects-form/', add_project, name='projects-form'),
    path('projects-form/<str:pk>/', edit_project, name='edit-project-form'),
    path('company-hub/', companyHub, name='company-hub'),
    path('project-hub/', projectHub, name='project-hub'),
    path('update-company-form/<str:pk>/',updateCompany, name='update-company-form'),
    path('delete-company-form/<str:pk>/',deleteCompany, name='delete-company-form'),
    path('update-project-form/<str:pk>/', edit_project, name='update-project-form'),
    path('update-student-form/<str:pk>/', edit_students, name='update-student-form'),
    path('delete-project-form/<str:pk>/', delete_project, name='delete-project-form'),
]