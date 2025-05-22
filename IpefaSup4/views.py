from datetime import datetime
from urllib import request

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from psycopg import IntegrityError
from .forms import LoginForm, StudentForm, TeacherForm, AdministratorForm, AddAcademicUEForm, AddUEForm, \
    StudentProfileForm, EducatorForm, TeacherProfileForm, StudentEditProfileForm, AddRegistrationForm, \
    AddParticipationForm, AddSessionForm, AddSectionForm, RegistrationApprovalForm
from .models import Educator, Student, Teacher, \
    Administrator, AcademicUE, Registration, Participation, Session, Section, UE
from .utils import get_logged_user_from_request
from django.utils.timezone import now




def welcome(request):
    logged_user = get_logged_user_from_request(request)

    if not logged_user:
        return redirect(reverse('login'))

    context = {
        'logged_user': logged_user,
        'current_date_time': now()
    }

    if logged_user.person_type == 'etudiant':
        context['student'] = logged_user
        return render(request, 'student/welcomeStudent.html', context)
    elif logged_user.person_type == 'professeur':
        return render(request, 'teacher/welcomeTeacher.html', context)
    elif isinstance(logged_user, Administrator):
        return render(request, 'administrator/welcomeAdmin.html', context)
    elif logged_user.person_type == 'educateur':
        return render(request, 'educator/welcomeEducator.html', context)
    else:
        return redirect(reverse('login'))



def login(request):
    if request.method == 'POST':
        form1 = LoginForm(request.POST)
        if form1.is_valid():
            user_email = form1.cleaned_data.get('email', '').strip()
            user_matricule = form1.cleaned_data.get('matricule', '').strip()
            password = form1.cleaned_data.get('password')

            # Connexion par email pour les étudiants
            if user_email:
                try:
                    logged_user = Student.objects.get(studentMail=user_email)
                    if check_password(password, logged_user.password):
                        request.session['logged_user_id'] = logged_user.id
                        request.session['person_type'] = 'etudiant'
                        return redirect(reverse('welcome'))  # Redirection avec reverse
                    else:
                        form1.add_error('password', 'Mot de passe incorrect.')
                except Student.DoesNotExist:
                    form1.add_error('email', 'Aucun étudiant trouvé avec cet email.')

            # Connexion par matricule pour les enseignants, éducateurs, administrateurs
            elif user_matricule:
                for model, type_name in [
                    (Educator, 'educateur'),
                    (Teacher, 'professeur'),
                    (Administrator, 'administrateur')
                ]:
                    try:
                        logged_user = model.objects.get(matricule=user_matricule)
                        if check_password(password, logged_user.password):
                            request.session['logged_user_id'] = logged_user.id
                            request.session['person_type'] = type_name
                            return redirect(reverse('welcome'))  # Redirection avec reverse
                        else:
                            form1.add_error('password', 'Mot de passe incorrect.')
                            break
                    except model.DoesNotExist:
                        continue
                else:
                    form1.add_error('matricule', 'Aucun utilisateur trouvé avec ce matricule.')

            # Si aucun email ni matricule n'est fourni
            else:
                form1.add_error(None, 'Veuillez entrer un email ou un matricule.')

        else:
            print("Formulaire invalide :", form1.errors)

        # Si le formulaire est invalide ou si des erreurs sont présentes
        return render(request, 'login.html', {'form1': form1})

    else:
        form1 = LoginForm()
        return render(request, 'login.html', {'form1': form1})





def register(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            if request.method == 'POST':
                # Créez les formulaires avec le préfixe
                studentForm = StudentForm(request.POST, prefix="st")
                teacherForm = TeacherForm(request.POST, prefix="te")
                educatorForm = EducatorForm(request.POST, prefix="ed")
                administratorForm = AdministratorForm(request.POST, prefix="ad")

                # Vérifiez quel type de profil a été sélectionné et sauvegardez le formulaire correspondant
                profile_type = request.POST.get('profileType')

                if profile_type == 'Student' and studentForm.is_valid():
                    studentForm.save()
                    return redirect('register')  # Redirigez après la création du compte
                elif profile_type == 'Teacher' and teacherForm.is_valid():
                    teacherForm.save()
                    return redirect('/register')
                elif profile_type == 'Educator' and educatorForm.is_valid():
                    educatorForm.save()
                    return redirect('/register')
                elif profile_type == 'Administrator' and administratorForm.is_valid():
                    administratorForm.save()
                    return redirect('/register')

                # Si aucun formulaire n'est valide ou si un autre problème se produit
                return render(request, 'user_profile.html', {
                    'studentForm': studentForm,
                    'teacherForm': teacherForm,
                    'educatorForm': educatorForm,
                    'administratorForm': administratorForm
                })

            else:
                # Si ce n'est pas un POST, renvoyez le formulaire avec le préfixe
                studentForm = StudentForm(prefix="st")
                teacherForm = TeacherForm(prefix="te")
                educatorForm = EducatorForm(prefix="ed")
                administratorForm = AdministratorForm(prefix="ad")

                return render(request, 'user_profile.html', {
                    'studentForm': studentForm,
                    'teacherForm': teacherForm,
                    'educatorForm': educatorForm,
                    'administratorForm': administratorForm
                })

        else:
            return redirect('login')
    else:
        return redirect('login')


def add_academic_ue_views(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            if request.method == 'POST':
                form = AddAcademicUEForm(request.POST)
                if form.is_valid():
                    form.save()  # Sauvegarde les données si le formulaire est valide
                    form = AddAcademicUEForm()
                    return render(request, 'administrator/add_academic_ue.html',
                                  {'form': form, 'success': True, 'logged_user': logged_user,
                                   'current_date_time': datetime.now})
            else:
                form = AddAcademicUEForm()
                return render(request, 'administrator/add_academic_ue.html',
                              {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')


def add_ue_views(request):
    logged_user = get_logged_user_from_request(request)

    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            if request.method == 'POST':
                form = AddUEForm(request.POST)
                if form.is_valid():
                    try:
                        form.save()
                        form = AddUEForm()  # Réinitialiser pour nouvel ajout
                        return render(request, 'administrator/add_ue.html', {
                            'form': form,
                            'success': True,
                            'logged_user': logged_user,
                            'current_date_time': datetime.now()
                        })
                    except Exception as e:
                        form.add_error(None, f"Erreur lors de l'enregistrement : {e}")
                        return render(request, 'administrator/add_ue.html', {
                            'form': form,
                            'logged_user': logged_user,
                            'current_date_time': datetime.now()
                        })
                else:
                    # Form invalide, renvoyer avec erreurs
                    return render(request, 'administrator/add_ue.html', {
                        'form': form,
                        'logged_user': logged_user,
                        'current_date_time': datetime.now()
                    })
            else:
                form = AddUEForm()
                return render(request, 'administrator/add_ue.html', {
                    'form': form,
                    'logged_user': logged_user,
                    'current_date_time': datetime.now()
                })
        else:
            return redirect('login')
    else:
        return redirect('login')



def add_registration_views(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            if request.method == 'POST':
                form = AddRegistrationForm(request.POST)
                if form.is_valid():
                    form.save()  # Sauvegarde les données si le formulaire est valide
                    form = AddRegistrationForm()
                    return render(request, 'administrator/registration.html',
                                  {'form': form, 'success': True, 'logged_user': logged_user, 'current_date_time': datetime.now})# Rediriger ou renvoyer une réponse après soumission
            else:
                form = AddRegistrationForm()  # Crée une nouvelle instance du formulaire
                return render(request, 'administrator/registration.html',
                          {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')



def add_participation_views(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur', 'professeur'):
            if request.method == 'POST':
                form = AddParticipationForm(request.POST)
                if form.is_valid():
                    form.save()  # Sauvegarde les données si le formulaire est valide
                    form = AddParticipationForm()
                    return render(request, 'administrator/participation.html',
                                  {'form': form,'success': True, 'logged_user': logged_user, 'current_date_time': datetime.now})
            # Re# Rediriger ou renvoyer une réponse après soumission
            else:
                form = AddParticipationForm()  # Crée une nouvelle instance du formulaire
                return render(request, 'administrator/participation.html',
                          {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')

def add_session_views(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            if request.method == 'POST':
                form = AddSessionForm(request.POST)
                if form.is_valid():
                    form.save()  # Sauvegarde les données si le formulaire est valide
                    form = AddSessionForm()
                    return render(request, 'administrator/session.html',
                                  {'form': form, 'success' :True})  # Re# Rediriger ou renvoyer une réponse après soumission
            else:
                form = AddSessionForm()  # Crée une nouvelle instance du formulaire
                return render(request, 'administrator/session.html',
                      {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')



def add_section_views(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            if request.method == 'POST':
                form = AddSectionForm(request.POST)
                wording = request.POST.get('wording').strip()

                if Section.objects.filter(wording=wording).exists():
                    pass
                else:
                    if form.is_valid():
                        form.save()

                        return render(request, 'administrator/session.html',
                                      {
                                          'form': form,
                                          'logged_user': logged_user,
                                          'current_date_time': datetime.now,
                                          'success': True
                                      })  # Assurez-vous que 'section' est le nom correct de l'URL
                    else:
                        return render(request, 'administrator/session.html',
                                      {'form':form,
                                                'logged_user': logged_user,
                                                'current_date_time': datetime.now})

                # Si le formulaire n'est pas valide ou si la section existe déjà, renvoyez le formulaire avec les erreurs
                return render(request, 'administrator/section.html', {
                    'form': form,
                    'logged_user': logged_user,
                    'current_date_time': datetime.now()
                })
            else:
                form = AddSectionForm()
                return render(request, 'administrator/section.html', {
                    'form': form,
                    'logged_user': logged_user,
                    'current_date_time': datetime.now()
                })
        else:
            return redirect('login')
    else:
        return redirect('login')




def student_list(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur', 'professeur'):
            sort_by = request.GET.get('sort_by', None)

            if sort_by == 'first_name':
                students = Student.objects.all().order_by('first_name')
            elif sort_by == 'last_name':
                students = Student.objects.all().order_by('last_name')
            else:
                students = Student.objects.all()

            return render(request, 'administrator/student_list.html',
                          {'students': students, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')




def edit_student(request, student_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            student = get_object_or_404(Student, id=student_id)

            if request.method == 'POST':
                form = StudentProfileForm(request.POST, instance=student)
                if form.is_valid():
                    form.save()  # Sauvegarder les modifications de l'étudiant
                    return redirect('student_list')  # Rediriger vers la liste après la mise à jour
            else:
                form = StudentProfileForm(instance=student)

            return render(request, 'administrator/edit_student.html',
                          {'form': form, 'student': student,
                           'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')



def teacher_list(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('administrateur', 'educateur'):
            sort_by = request.GET.get('sort_by')

            if sort_by == 'first_name':
                teachers = Teacher.objects.all().order_by('first_name')
            elif sort_by == 'last_name':
                teachers = Teacher.objects.all().order_by('last_name')
            else:
                teachers = Teacher.objects.all()

            return render(request, 'administrator/teacher_list.html', {
                'teachers': teachers,
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
            })
        else:
            return redirect('login')
    else:
        return redirect('login')

def edit_teacher(request, teacher_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'administrateur':
            teacher = get_object_or_404(Teacher, id=teacher_id)

            if request.method == 'POST':
                form = TeacherProfileForm(request.POST, instance=teacher)
                if form.is_valid():
                    form.save()  # Sauvegarder les modifications de l'étudiant
                    return redirect('teacher_list')  # Rediriger vers la liste après la mise à jour
            else:
                form = TeacherProfileForm(instance=teacher)

            return render(request, 'administrator/edit_teacher.html', {'form': form, 'teacher': teacher, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')


def edit_own_profile(request):
    logged_user = get_logged_user_from_request(request)  # Méthode que tu utilises déjà
    if logged_user:
        if logged_user.person_type == 'etudiant':

            student = get_object_or_404(Student, id=logged_user.id)

            if request.method == 'POST':
                form = StudentEditProfileForm(request.POST, instance=student)
                if form.is_valid():
                    student_instance = form.save(commit=False)
                    # Conserve le mot de passe actuel
                    student_instance.password = student.password
                    student_instance.save()
                    return redirect('/welcome')  # Ou une autre page de confirmation
                else:
                    # Tu peux ajouter un message ou un log ici si nécessaire
                    pass
            else:
                form = StudentEditProfileForm(instance=student)

            return render(request, 'student/edit_profile.html', {
                'form': form,
                'student': student,
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
            })
        else:
            return redirect('login')
    else:
        return redirect('login')




def student_registration_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'etudiant':

            registrations = logged_user.registrations.all()

            return render(request, 'student/student_registration.html', {
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'registrations': registrations,
            })


def student_non_passed_registrations_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'etudiant':

            non_passed_registrations = logged_user.registrations.filter(status='NP')

            return render(request, 'student/student_non_passed_registrations.html', {
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'registrations': non_passed_registrations,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')


def student_passed_registrations_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'etudiant':

            # On récupère seulement les inscriptions avec status = 'AP' (Approuvé)
            registrations = logged_user.registrations.select_related('academic_ue', 'academic_ue__section').filter(status='AP')

            return render(request, 'student/student_passed_registrations.html', {
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'registrations': registrations,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')








def student_prerequisites_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'etudiant':
            # Récupérer toutes ses inscriptions
            registrations = logged_user.registrations.select_related('academic_ue', 'academic_ue__section').all()

            # Créer une liste des UE et de leurs prérequis
            ue_with_prerequisites = []
            for registration in registrations:
                ue = registration.academic_ue
                prerequisites = ue.prerequisites.all() if hasattr(ue, 'prerequisites') else []  # .prerequisites si relation ManyToManyField
                ue_with_prerequisites.append({
                    'ue': ue,
                    'prerequisites': prerequisites
                })

            return render(request, 'student/student_prerequisites.html', {
                'student': logged_user,
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'ue_with_prerequisites': ue_with_prerequisites,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')



def teacher_academic_ues(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'professeur':

            academic_ues = AcademicUE.objects.filter(teacher=logged_user)

            return render(request, 'teacher/teacher_academic_ues.html', {
                'teacher': logged_user,
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'academic_ues': academic_ues,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')





def academic_ues_for_teacher(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'professeur':
            # Récupère les unités académiques du professeur connecté
            academic_ues = AcademicUE.objects.filter(teacher=logged_user)
            return render(request, 'teacher/academic_ues_list.html', {
                'academic_ues': academic_ues,
                'logged_user': logged_user,
                'current_date_time': datetime.now()
            })
        else:
            return redirect('login')
    else:
        return redirect('login')

def students_in_academic_ue(request, academic_ue_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'professeur':
            # Récupère l'unité académique spécifique et ses inscriptions
            academic_ue = get_object_or_404(AcademicUE, idUE=academic_ue_id)
            registrations = Registration.objects.filter(academic_ue=academic_ue)
            return render(request, 'teacher/students_in_ue.html', {
                'academic_ue': academic_ue,
                'registrations': registrations,
                'logged_user': logged_user,
                'current_date_time': datetime.now()
            })
        else:
            return redirect('login')
    else:
        return redirect('login')


def encode_results(request, academic_ue_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'professeur':
            academic_ue = get_object_or_404(AcademicUE, idUE=academic_ue_id)

            if request.method == 'POST':
                registrations = Registration.objects.filter(academic_ue=academic_ue)
                for registration in registrations:
                    result = request.POST.get(f'result_{registration.id}')
                    status = request.POST.get(f'status_{registration.id}')
                    if result:
                        registration.result = result
                    if status:
                        registration.status = status
                    registration.save()

                # Recharger les enregistrements à jour depuis la BDD
                registrations = Registration.objects.filter(academic_ue=academic_ue)

            else:
                registrations = Registration.objects.filter(academic_ue=academic_ue)

            return render(request, 'teacher/encode_results.html', {
                'academic_ue': academic_ue,
                'registrations': registrations,
                'logged_user': logged_user,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')



def student_participation_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'etudiant':

            # Récupérer les UEs auxquelles l'étudiant est inscrit
            academic_ues = logged_user.academic_ues.all()

            # Si un filtre (academic_ue_id) est passé dans la requête, on filtre les participations
            selected_academic_ue = None
            participations = None

            # Vérifier si un ID d'UE est passé dans la requête GET
            if request.method == 'GET' and 'academic_ue' in request.GET and request.GET['academic_ue']:
                try:
                    selected_academic_ue = AcademicUE.objects.get(id=request.GET['academic_ue'])
                    participations = Participation.objects.filter(
                        student=logged_user,
                        session__academicUE=selected_academic_ue
                    ).select_related('session', 'session__academicUE')
                except AcademicUE.DoesNotExist:
                    participations = []
            else:
                # Si aucun filtre n'est passé, afficher toutes les participations de l'étudiant
                participations = Participation.objects.filter(student=logged_user).select_related('session', 'session__academicUE')

            return render(request, 'student/student_participation.html', {
                'student': logged_user,
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'participations': participations,
                'academic_ues': academic_ues,  # Passer les UE de l'étudiant pour le filtrage
                'selected_academic_ue': selected_academic_ue  # Passer l'UE sélectionné pour la gestion de l'affichage
            })
        else:
            return redirect('login')
    else:
        return redirect('login')





def participations_in_ue(request, academic_ue_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type == 'professeur':
            academic_ue = get_object_or_404(AcademicUE, idUE=academic_ue_id, teacher=logged_user)
            sessions = academic_ue.sessions.all()
            students = Student.objects.filter(registrations__academic_ue=academic_ue).distinct()

            allowed_statuses = {"P", "M", "A"}  # Seuls les statuts autorisés pour un professeur

            if request.method == 'POST':
                for key, value in request.POST.items():
                    if key.startswith('status_'):
                        parts = key.split('_')  # format attendu: status_<session_id>_<student_id>
                        if len(parts) == 3:
                            _, session_id, student_id = parts
                            try:
                                session = Session.objects.get(id=session_id)
                                student = Student.objects.get(id=student_id)

                                participation = Participation.objects.filter(session=session, student=student).first()

                                if value in allowed_statuses:
                                    if not participation:
                                        participation = Participation(session=session, student=student)
                                    participation.status = value
                                    participation.save()
                                elif participation:
                                    # Si l'utilisateur efface le statut, on supprime la participation
                                    participation.delete()

                            except (Session.DoesNotExist, Student.DoesNotExist):
                                continue  # Ignore si la session ou l'étudiant est introuvable

                messages.success(request, "Participations mises à jour avec succès.")
                return redirect('participations_in_ue', academic_ue_id=academic_ue_id)

            session_data = []
            for session in sessions:
                row = {
                    'session': session,
                    'participations': []
                }
                for student in students:
                    participation = Participation.objects.filter(session=session, student=student).first()
                    row['participations'].append({
                        'student': student,
                        'logged_user': logged_user,
                        'participation': participation  # Peut être None si non existant
                    })
                session_data.append(row)

            # Préparer la liste unique des étudiants pour le filtre
            all_students = sorted(
                students,
                key=lambda s: (s.last_name.lower(), s.first_name.lower())
            )

            return render(request, 'teacher/participations_in_ue.html', {
                'academic_ue': academic_ue,
                'session_data': session_data,
                'status_choices': [choice for choice in Participation._meta.get_field('status').choices if choice[0] in allowed_statuses],
                'students': all_students,  # Pour le filtre dans le template
                'logged_user': logged_user,
                'current_date_time': datetime.now
            })
        else:
            return redirect('login')
    else:
        return redirect('login')


def student_manage_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            return render(request, 'educator/student_manage.html', {
                'logged_user': logged_user, 'current_date_time': datetime.now()
            })
        else:
            return redirect('login')
    else:
        return redirect('login')


from django.shortcuts import render, redirect
from datetime import datetime
from .models import Student
from .forms import StudentForm, StudentProfileForm
from .utils import get_logged_user_from_request  # selon où est ta fonction

def add_student_view(request):
    logged_user = get_logged_user_from_request(request)

    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            if request.method == 'POST':
                form = StudentProfileForm(request.POST)
                studentMail = request.POST.get('studentMail', '').strip()

                if not Student.objects.filter(studentMail=studentMail).exists():
                    if form.is_valid():
                        form.save()
                        success = True
                    else:
                        success = False
                else:
                    success = False  # adresse déjà utilisée

                # Formulaire vierge pour retour
                new_form = StudentForm()
                return render(request, 'educator/add_student.html', {
                    'form': new_form,
                    'logged_user': logged_user,
                    'current_date_time': datetime.now(),
                    'success': success
                })

            else:
                form = StudentForm()

            return render(request, 'educator/add_student.html', {
                'form': form,
                'logged_user': logged_user,
                'current_date_time': datetime.now()
            })
        return redirect('login')

    return redirect('login')



def ue_manage_view(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            return render(request, 'educator/ue_manage.html', {
                'logged_user': logged_user,
                'current_date_time': datetime.now()
            })
        else:
            return redirect('login')
    else:
        return redirect('login')

def select_section(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            sections = Section.objects.all()
            return render(request, 'educator/select_section.html', {'sections': sections})
        else:
            return redirect('login')
    else:
        return redirect('login')


def ues_by_section(request, section_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            section = get_object_or_404(Section, id=section_id)
            ues = section.ues.all()  # grâce au related_name='ues' dans le modèle UE
            return render(request, 'educator/ues_by_section.html', {'section': section, 'ues': ues})
        else:
            return redirect('login')
    else:
        return redirect('login')


def ue_detail(request, ue_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            ue = get_object_or_404(AcademicUE, idUE=ue_id)
            sessions = Session.objects.filter(academicUE=ue)
            return render(request, 'educator/ue_details.html', {
                    'ue': ue,
                    'sessions': sessions,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')



def manage_sessions(request, ue_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            academic_ue = get_object_or_404(AcademicUE, idUE=ue_id)

            if request.method == 'POST':
                session_id = request.POST.get('session_id')
                jour = request.POST.get('jour')
                mois = request.POST.get('mois')

                if jour and mois:
                    jour = int(jour)
                    mois = int(mois)

                    if session_id:  # Modifier une session existante
                        session = get_object_or_404(Session, id=session_id)
                        session.jour = jour
                        session.mois = mois
                        session.save()
                    else:  # Créer une nouvelle session
                        Session.objects.create(academicUE=academic_ue, jour=jour, mois=mois)

                return redirect('manage_sessions', ue_id=academic_ue.idUE)

            sessions = Session.objects.filter(academicUE=academic_ue)

            return render(request, 'educator/manage_sessions.html', {
                'academic_ue': academic_ue,  # pour générer les liens dans le template
                'sessions': sessions,
                'logged_user': logged_user,
                'current_date_time': now()
            })
        else:
            return redirect('login')
    else:
        return redirect('login')



def edit_session(request, session_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):
            session = get_object_or_404(Session, id=session_id)
            if request.method == 'POST':
                # Récupérer les nouvelles valeurs depuis le formulaire
                jour = request.POST.get('jour')
                mois = request.POST.get('mois')

                if jour and mois:
                    session.jour = int(jour)
                    session.mois = int(mois)
                    session.save()
                    return redirect('manage_sessions', ue_id=session.academicUE.idUE)

            return render(request, 'educator/edit_session.html', {
                'session': session,
                'logged_user': logged_user,
                'current_date_time': datetime.now
            })
        else:
            return redirect('login')
    else:
        return redirect('login')





def manage_participations_in_ue(request, academic_ue_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            academic_ue = get_object_or_404(AcademicUE, idUE=academic_ue_id)
            sessions = academic_ue.sessions.all()
            students = Student.objects.filter(registrations__academic_ue=academic_ue).distinct()

            allowed_statuses = {"abandon", "CM", "dispense"}  # Statuts autorisés

            if request.method == 'POST':
                for key, value in request.POST.items():
                    if key.startswith('status_'):
                        parts = key.split('_')  # format attendu: status_<session_id>_<student_id>
                        if len(parts) == 3:
                            _, session_id, student_id = parts
                            try:
                                session = Session.objects.get(id=session_id)
                                student = Student.objects.get(id=student_id)

                                participation = Participation.objects.filter(session=session, student=student).first()

                                if value in allowed_statuses:
                                    if not participation:
                                        participation = Participation(session=session, student=student)
                                    participation.status = value
                                    participation.save()
                                elif participation:
                                    participation.delete()

                            except (Session.DoesNotExist, Student.DoesNotExist):
                                continue

                messages.success(request, "Participations mises à jour avec succès.")
                return redirect('manage_participations_in_ue', academic_ue_id=academic_ue_id)

            session_data = []
            for session in sessions:
                row = {
                    'session': session,
                    'participations': []
                }
                for student in students:
                    participation = Participation.objects.filter(session=session, student=student).first()
                    row['participations'].append({
                        'student': student,
                        'participation': participation
                    })
                session_data.append(row)

            all_students = sorted(
                students,
                key=lambda s: (s.last_name.lower(), s.first_name.lower())
            )

            return render(request, 'educator/manage_participations_in_ue.html', {
                'academic_ue': academic_ue,
                'session_data': session_data,
                'status_choices': [choice for choice in Participation._meta.get_field('status').choices if choice[0] in allowed_statuses],
                'students': all_students,
                'logged_user': logged_user,
                'current_date_time': datetime.now,
                'ue': academic_ue,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')





# Liste des sections accessibles par l'éducateur ou l'administrateur



# Liste des sections accessibles par l'éducateur ou l'administrateur
def section_list(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            sections = Section.objects.all()
            return render(request, 'educator/section_list.html', {'sections': sections,   'logged_user': logged_user,
                'current_date_time': now()})
        else:
            return redirect('login')
    else:
        return redirect('login')



def registration_list(request, section_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            section = get_object_or_404(Section, pk=section_id)

            registrations = Registration.objects.filter(
                academic_ue__section=section
            ).select_related(
                'student', 'academic_ue'
            ).prefetch_related(
                'academic_ue__prerequisites'
            )

            # Extraire les noms uniques des étudiants
            student_names = sorted(set(
                f"{r.student.first_name} {r.student.last_name}" for r in registrations
            ))

            # Extraire les emails uniques des étudiants (utilisation de 'student.email' au lieu de 'student.studentMail')
            student_mail = sorted(set(
                r.student.studentMail for r in registrations if r.student.studentMail  # Utiliser r.student.email pour accéder à l'email
            ))

            # Extraire les statuts uniques
            statuses = sorted(set(r.status for r in registrations))

            # Extraire les UE uniques
            ue_wordings = sorted(set(r.academic_ue.wording for r in registrations))

            # Extraire les prérequis uniques
            prereqs = set()
            for r in registrations:
                for prereq in r.academic_ue.prerequisites.all():
                    prereqs.add(prereq.wording)
            prereq_wordings = sorted(prereqs)

            return render(request, 'educator/registration_list.html', {
                'logged_user': logged_user,
                'current_date_time': now(),
                'section': section,
                'registrations': registrations,
                'student_names': student_names,
                'studentMail': student_mail,  # Corrigé ici : 'studentMail' contiendra maintenant les emails
                'statuses': statuses,
                'ue_wordings': ue_wordings,
                'prereq_wordings': prereq_wordings,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')







def add_registration(request, section_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            section = get_object_or_404(Section, id=section_id)
            students = Student.objects.all()  # Optionnel : filtrer par section
            academic_ues = AcademicUE.objects.filter(section=section)

            selected_student_id = None
            selected_ue_id = None

            if request.method == 'POST':
                selected_student_id = request.POST.get('student')
                selected_ue_id = request.POST.get('academic_ue')

                if selected_student_id and selected_ue_id:
                    student = get_object_or_404(Student, id=selected_student_id)
                    academic_ue = get_object_or_404(AcademicUE, id=selected_ue_id)

                    prerequisites = academic_ue.prerequisites.all()
                    all_prerequisites_passed = True

                    for prereq in prerequisites:
                        try:
                            reg = Registration.objects.get(student=student, academic_ue=prereq)
                            if not reg.approved or reg.status != "AP":
                                all_prerequisites_passed = False
                                break
                        except Registration.DoesNotExist:
                            all_prerequisites_passed = False
                            break

                    if all_prerequisites_passed or not prerequisites.exists():
                        registration, created = Registration.objects.get_or_create(
                            student=student,
                            academic_ue=academic_ue,
                            defaults={
                                'approved': False,
                                'status': "NP",
                                'result': None
                            }
                        )
                        if all_prerequisites_passed or not prerequisites.exists():
                            # Récupère toutes les sessions de cette UE
                            total_sessions = academic_ue.sessions.count()
                            if total_sessions > 0:
                                sessions_with_participation = Participation.objects.filter(
                                    session__in=academic_ue.sessions.all()
                                ).exclude(status__isnull=True).distinct().count()

                                ratio = sessions_with_participation / total_sessions
                                if ratio >= 0.4:
                                    messages.error(request,
                                                   "Il est trop tard pour s'inscrire : plus de 40% des sessions ont déjà eu lieu.")

                        if created:
                            messages.success(request, "L'inscription a été ajoutée avec succès.")
                            selected_student_id = None
                            selected_ue_id = None
                        else:
                            messages.info(request, "L'étudiant est déjà inscrit à cette UE.")
                    else:
                        messages.error(request, "Les prérequis ne sont pas remplis.")
                else:
                    messages.error(request, "Veuillez sélectionner un étudiant et une UE.")

            return render(request, 'educator/add_registration.html', {
                'students': students,
                'academic_ues': academic_ues,
                'section': section,
                'selected_student_id': selected_student_id,
                'selected_ue_id': selected_ue_id,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')



def add_registrations_by_cycle(request, section_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            section = get_object_or_404(Section, pk=section_id)
            students = Student.objects.all()

            if request.method == 'POST':
                student_id = request.POST.get('student')
                year_cycle = request.POST.get('year_cycle')

                if not student_id or not year_cycle:
                    messages.error(request, "Veuillez sélectionner un étudiant et un cycle.")
                    return redirect('add_registrations_by_cycle', section_id=section.id)

                student = get_object_or_404(Student, pk=student_id)
                year_cycle = int(year_cycle)

                academic_ues = AcademicUE.objects.filter(section=section, yearCycle=year_cycle)

                created_count = 0
                for ue in academic_ues:
                    try:
                        Registration.objects.create(student=student, academic_ue=ue)
                        created_count += 1
                    except IntegrityError:
                        # Ignore duplicate registration
                        pass

                messages.success(request, f"{created_count} inscriptions ajoutées pour {student.first_name} {student.last_name}.")
                return redirect('registration_list', section_id=section.id)

            return render(request, 'educator/add_registrations_by_cycle.html', {
                'students': students,
                'section': section,
                'logged_user': logged_user,
                'current_date_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        else:
            return redirect('login')
    else:
        return redirect('login')


def participations_view(request, id_ue):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur', 'professeur'):

                academicue = get_object_or_404(AcademicUE, idUE=id_ue)

                participations = []
                for session in academicue.sessions.all():
                    for p in session.participations.all():
                        participations.append({
                            "Étudiant": str(p.student),
                            "Session": f"{session.jour}/{session.mois}",
                            "UE": f"{academicue.idUE} - {academicue.wording}",
                            "Statut": p.get_status_display()
                        })

                return render(request, "educator/participations.html", {
                    "academicue": academicue,
                    "participations": participations
                })
        else:
            return redirect('login')
    else:
        return redirect('login')




def check_student_mail(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            student_mail = data.get('studentMail', '').strip()

            if not student_mail:
                return JsonResponse({'exists': False, 'error': 'Adresse email manquante'})

            exists = Student.objects.filter(studentMail=student_mail).exists()

            return JsonResponse({
                'exists': exists,
                'message': 'Cette adresse mail existe déjà' if exists else "Adresse disponible"
            })

        except json.JSONDecodeError:
            return JsonResponse({'exists': False, 'error': 'Requête invalide'}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def check_employee_email(request):
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            employee_email = data.get('employee_email', '').strip()

            if not employee_email:
                return JsonResponse({'exists': False, 'error': 'Adresse email manquante'})

            exists = (
                Educator.objects.filter(employee_email=employee_email).exists() or
                Teacher.objects.filter(employee_email=employee_email).exists() or
                Administrator.objects.filter(employee_email=employee_email).exists()
            )

            return JsonResponse({
                'exists': exists,
                'message': 'Cette adresse mail existe déjà' if exists else 'Adresse disponible'
            })

        except json.JSONDecodeError:
            return JsonResponse({'exists': False, 'error': 'Requête invalide'}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def check_matricule(request):
    import json
    if request.method == 'POST':
        data = json.loads(request.body)
        matricule = data.get('matricule')

        exists = Teacher.objects.filter(matricule=matricule).exists() or \
                 Educator.objects.filter(matricule=matricule).exists() or \
                 Administrator.objects.filter(matricule=matricule).exists()

        return JsonResponse({'exists': exists})

    return JsonResponse({'exists': False})

def check_registration(request):
    student_id = request.GET.get('student_id')
    ue_id = request.GET.get('ue_id')

    exists = Registration.objects.filter(student_id=student_id, academic_ue_id=ue_id).exists()
    return JsonResponse({'registered': exists})




def check_section(request):
    import json
    try:
        # Lire les données JSON envoyées dans la requête
        data = json.loads(request.body)
        wording = data.get('wording', '').strip()

        # Vérifier si la section existe déjà
        exists = Section.objects.filter(wording=wording).exists()

        return JsonResponse({'exists': exists})
    except json.JSONDecodeError:
        # En cas d'erreur de décodage JSON, renvoyer une réponse par défaut
        return JsonResponse({'exists': False})



def check_ue_session_progress(request):
    ue_id = request.GET.get('ue_id')
    if ue_id:
        try:
            ue = AcademicUE.objects.get(id=ue_id)
            total_sessions = ue.sessions.count()
            sessions_with_participation = Participation.objects.filter(
                session__in=ue.sessions.all()
            ).exclude(status__isnull=True).distinct().count()

            if total_sessions > 0:
                ratio = sessions_with_participation / total_sessions
            else:
                ratio = 0

            return JsonResponse({'too_late': ratio >= 0.4, 'ratio': ratio})
        except AcademicUE.DoesNotExist:
            return JsonResponse({'error': 'UE introuvable'}, status=404)
    return JsonResponse({'error': 'Paramètre manquant'}, status=400)




def get_ue_info(request, ue_id):
    try:
        ue = UE.objects.get(pk=ue_id)
        # Vérifie si une AcademicUE existe pour cette UE
        try:
            academic_ue = AcademicUE.objects.get(pk=ue_id)
        except AcademicUE.DoesNotExist:
            academic_ue = None

        # Prépare les données
        data = {
            'idUE': ue.idUE,
            'wording': ue.wording,
            'numberPeriods': ue.numberPeriods,
            'section': ue.section.id if ue.section else None,
            'section_name': str(ue.section) if ue.section else "",
            'prerequisites': list(ue.prerequisites.values_list('id', flat=True)),
            'academicUE': {},
        }

        if academic_ue:
            data['academicUE'] = {
                'academicYear': academic_ue.academicYear,
                'yearCycle': academic_ue.yearCycle,
                'teacher': academic_ue.teacher.id if academic_ue.teacher else None,
                'teacher_name': str(academic_ue.teacher) if academic_ue.teacher else "",
                'educator': academic_ue.educator.id if academic_ue.educator else None,
                'educator_name': str(academic_ue.educator) if academic_ue.educator else "",
            }

        return JsonResponse(data)

    except UE.DoesNotExist:
        return JsonResponse({'error': 'UE non trouvée'}, status=404)



def ue_info(request, ue_id):
    try:
        ue = UE.objects.get(idUE=ue_id)
        data = {
            'wording': ue.wording,
            'numberPeriods': ue.numberPeriods,
            'section': ue.section.id if ue.section else None
        }
        return JsonResponse(data)
    except UE.DoesNotExist:
        raise Http404("UE non trouvée")





def approve_result_view(request, registration_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ('educateur', 'administrateur'):

            registration = get_object_or_404(Registration, id=registration_id)

            if request.method == 'POST':
                form = RegistrationApprovalForm(request.POST, instance=registration)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Résultat approuvé avec succès.")
                    # Redirige vers la même page pour afficher le message
                    return redirect('approve_result', registration_id=registration_id)
            else:
                form = RegistrationApprovalForm(instance=registration)

            context = {
                'form': form,
                'logged_user': logged_user,
                'current_date_time': datetime.now(),
                'registration': registration,
                'student_name': f"{registration.student.first_name} {registration.student.last_name}",
                'academic_ue_name': registration.academic_ue.wording,
                'section_id': registration.academic_ue.section.id
            }

            return render(request, 'educator/approve_result.html', context)
        else:
            return redirect('login')
    else:
        return redirect('login')




def list_approved_students(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if logged_user.person_type in ( 'educateur', 'administrateur'):

            # Filtrer les inscriptions où l'étudiant a une UE avec status AP et approved True
            registrations = Registration.objects.filter(
                status='AP',
                approved=True
            ).select_related('student', 'academic_ue')

            return render(request, 'educator/list_approved_students.html', {
                'registrations': registrations,
                'logged_user': logged_user,
                'current_date_time': datetime.now,
            })
        else:
            return redirect('login')
    else:
        return redirect('login')