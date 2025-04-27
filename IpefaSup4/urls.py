"""
URL configuration for IpefaSup4 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path


from django.urls import path
from .views import login, welcome, register, add_academic_ue_views, add_ue_views, student_list, edit_student, \
    teacher_list, edit_teacher, edit_own_profile, add_registration_views, add_participation_views, \
    add_session_views, add_section_views, student_registration_view, teacher_academic_ues, \
    student_non_passed_registrations_view, student_passed_registrations_view, student_prerequisites_view, \
    academic_ues_for_teacher, students_in_academic_ue
from django.contrib import admin

urlpatterns = [
    path('', login, name='login'),
    path('login/', login, name='login'),  # Path pour la connexion
    path('welcome/', welcome, name='welcome'),  # Accueil générique
    path('user_profile/', register, name='user_profile'),  # Profil utilisateur
    path('register/', register, name='register'),  # Inscription




    path('welcomeStudent/', welcome, name='welcomeStudent'),
    path('edit/', edit_own_profile, name='edit_own_profile'),
    path ('student/student_registration', student_registration_view, name='student_registration' ),

    path('student/non_passed_registrations/', student_non_passed_registrations_view,
         name='student_non_passed_registrations'),
    path('student/passed_registrations/', student_passed_registrations_view, name='student_passed_registrations'),

    path('student/prerequisites/', student_prerequisites_view, name='student_prerequisites'),





    path('welcomeTeacher/', welcome, name='welcomeTeacher'),
    path('teacher/teacher_academic_ues/', teacher_academic_ues, name='teacher_academic_ues'),

    path('teacher/academic-ues/', academic_ues_for_teacher, name='academic_ue_for_teacher'),

    path('welcomeTeacher/students-in-ue/<str:academic_ue_id>/', students_in_academic_ue, name='students_in_academic_ue'),





    # Accueil éducateur
    path('welcomeEducator/', welcome, name='welcomeEducator'),



    # Accueil administrator

    path('welcomeAdministrator/add_academic_ue/', add_academic_ue_views, name='add_academic_ue'),  # Ajouter UE académique

    path('welcomeAdministrator/add_ue/', add_ue_views, name='add_ue'),  # Ajouter UE

    path('welcomeAdministrator/registration/', add_registration_views, name='registration'),  # A

    path('welcomeAdministrator/section/', add_section_views, name='section'),  # A

    path('welcomeAdministrator/session/', add_session_views, name='session'),  # A

    path('welcomeAdministrator/participation/', add_participation_views, name='participation'),  # A

    path('welcomeAdministrator/students/', student_list, name='student_list'),  # Liste des étudiants

    path('welcomeAdministrator/students/edit/<int:student_id>/', edit_student, name='edit_student'),  # Modifier un étudiant

    path('welcomeAdministrator/teacher_list/', teacher_list, name='teacher_list'),  # Liste des professeurs

    path('welcomeAdministrator/teacher/edit/<int:teacher_id>/', edit_teacher, name='edit_teacher'),  # Modifier un professeur







    path('admin/', admin.site.urls),  # Admin Django
]
