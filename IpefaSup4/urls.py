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
    academic_ues_for_teacher, students_in_academic_ue, encode_results, \
    participations_in_ue, student_participation_view, student_manage_view, add_student_view, ue_manage_view, \
    select_section, ues_by_section, ue_detail, manage_sessions, edit_session, manage_participations_in_ue, section_list, \
    add_registration, registration_list, add_registrations_by_cycle, participations_view, check_student_mail, \
    check_matricule, approve_result_view, list_approved_students, check_employee_email, check_section, \
    check_registration, check_ue_session_progress, get_ue_info, ue_info, check_student_registration
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

    path('student/participations/', student_participation_view, name='student_participation'),





    path('welcomeTeacher/', welcome, name='welcomeTeacher'),
    path('teacher/teacher_academic_ues/', teacher_academic_ues, name='teacher_academic_ues'),

    path('teacher/academic-ues/', academic_ues_for_teacher, name='academic_ue_for_teacher'),

    path('teacher/students-in-ue/<str:academic_ue_id>/', students_in_academic_ue, name='students_in_academic_ue'),

    path('teacher/encode_results/<str:academic_ue_id>/', encode_results, name='encode_results'),

    path('teacher/academic_ue/<str:academic_ue_id>/participations/', participations_in_ue, name='participations_in_ue'),







    # Accueil éducateur
    path('welcomeEducator/', welcome, name='welcomeEducator'),  # Page de bienvenue pour l'éducateur

    # Gestion des étudiants (chemin unique pour chaque vue)
    path('educator/students/', student_manage_view, name='student_manage'),

    # Gestion des UEs (chemin unique pour chaque vue)
    path('educator/ues/', ue_manage_view, name='ue_manage'),

    # Ajouter un étudiant (chemin unique pour l'ajout d'un étudiant)
    path('educator/students/add/', add_student_view, name='add_student'),

    # Sélection de la section
    path('educator/sections/', select_section, name='select_section'),

    # Lister les UEs par section
    path('educator/sections/<int:section_id>/ues/', ues_by_section, name='ues_by_section'),

    path('educator/ues/<str:ue_id>/', ue_detail, name='ue_details'),  # Détail de l'UE

    path('educator/ues/<int:ue_id>/sessions/', manage_sessions, name='manage_sessions'),
    path('educator/sessions/edit/<int:session_id>/', edit_session, name='edit_session'),

    path('educator/ue/<int:academic_ue_id>/participations/', manage_participations_in_ue, name='manage_participations_in_ue'),

    path('educator/sections-list/', section_list, name='section_list'),
    path('educator/sections/<int:section_id>/registrations/', registration_list, name='registration_list'),
    path('section/<int:section_id>/add_registration/', add_registration, name='add_registration'),

    path('section/<int:section_id>/add_registrations_by_cycle/', add_registrations_by_cycle, name='add_registrations_by_cycle'),

    path("academicue/<str:id_ue>/participations/", participations_view, name="academicue_participations"),

    path('api/check_student_mail/', check_student_mail, name='check_student_mail'),

    path('api/check-matricule/', check_matricule, name='check_matricule'),

    path('check-section/', check_section, name='check_section'),

    path('api/check_employee_email/', check_employee_email, name='check_employee_email'),

    path('api/check-registration/', check_registration, name='check_registration'),

    path('api/check-ue-progress/', check_ue_session_progress, name='check_ue_progress'),

    path('ajax/check-student-registration/', check_student_registration, name='check_student_registration'),

    path('ue-info/<str:ue_id>/', get_ue_info, name='ue_info'),

    path('ue-info/<str:ue_id>/', ue_info, name='ue_info'),
    path('registration/<int:registration_id>/approve/', approve_result_view, name='approve_result'),

    path('educator/list-approved-students/', list_approved_students, name='list_approved_students'),







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
