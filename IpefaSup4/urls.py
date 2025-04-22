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
    teacher_list, edit_teacher, edit_own_profile, list_student_ues
from django.contrib import admin

urlpatterns = [
    path('', login, name='login'),
    path('login/', login, name='login'),  # Path pour la connexion
    path('welcome/', welcome, name='welcome'),  # Accueil générique
    path('user_profile/', register, name='user_profile'),  # Profil utilisateur
    path('register/', register, name='register'),  # Inscription


    path('welcomeStudent/', welcome, name='welcomeStudent'),
    path('edit/', edit_own_profile, name='edit_own_profile'),
    path('list-ues/', list_student_ues, name='list_student_ues'),



    path('welcomeTeacher/', welcome, name='welcomeTeacher'),


    # Accueil professeur
    path('welcomeEducator/', welcome, name='welcomeEducator'),



    # Accueil éducateur
    path('welcomeAdministrator/add_academic_ue/', add_academic_ue_views, name='add_academic_ue'),  # Ajouter UE académique
    path('welcomeAdministrator/add_ue/', add_ue_views, name='add_ue'),  # Ajouter UE
    path('admin/students/', student_list, name='student_list'),  # Liste des étudiants
    path('admin/students/edit/<int:student_id>/', edit_student, name='edit_student'),  # Modifier un étudiant
    path('admin/teacher_list/', teacher_list, name='teacher_list'),  # Liste des professeurs
    path('admin/teacher/edit/<int:teacher_id>/', edit_teacher, name='edit_teacher'),  # Modifier un professeur
    path('admin/', admin.site.urls),  # Admin Django
]
