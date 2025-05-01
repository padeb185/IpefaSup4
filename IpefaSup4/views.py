from datetime import datetime

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import LoginForm, StudentForm, TeacherForm, AdministratorForm, AddAcademicUEForm, AddUEForm, \
    StudentProfileForm, EducatorForm, TeacherProfileForm, StudentEditProfileForm, AddRegistrationForm, \
    AddParticipationForm, AddSessionForm, AddSectionForm
from .models import Educator, Student, Teacher, \
    Administrator, AcademicUE, Registration, Participation, Session
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
            return redirect('/welcome')  # Redirigez après la création du compte
        elif profile_type == 'Teacher' and teacherForm.is_valid():
            teacherForm.save()
            return redirect('/welcome')
        elif profile_type == 'Educator' and educatorForm.is_valid():
            educatorForm.save()
            return redirect('/welcome')
        elif profile_type == 'Administrator' and administratorForm.is_valid():
            administratorForm.save()
            return redirect('/welcome')

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
                    form.save()  # Sauvegarde les données si le formulaire est valide
                    form = AddUEForm()
                    return render(request, 'administrator/add_ue.html',
                                  {'form': form, 'success': True, 'logged_user': logged_user, 'current_date_time': datetime.now})
            else:
                form = AddUEForm()
                return render(request, 'administrator/add_ue.html',
                              {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})
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
                if form.is_valid():
                    form.save() # Sauvegarde les données si le formulaire est valide
                    form = AddSectionForm()
                    return render(request, 'administrator/section.html',
                                  {'form': form, 'success': True,
                                            'logged_user': logged_user, 'current_date_time': datetime.now})  # Re# Rediriger ou renvoyer une réponse après soumission
            else:
                form = AddSectionForm()
                return render(request, 'administrator/section.html',
                      {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})
        else:
            return redirect('login')
    else:
        return redirect('login')



def student_list(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        sort_by = request.GET.get('sort_by', None)

        if sort_by == 'first_name':
            students = Student.objects.all().order_by('first_name')
        elif sort_by == 'last_name':
            students = Student.objects.all().order_by('last_name')
        else:
            students = Student.objects.all()

        return render(request, 'administrator/student_list.html',
                      {'students': students, 'logged_user': logged_user, 'current_date_time': datetime.now})

def edit_student(request, student_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        student = get_object_or_404(Student, id=student_id)

        if request.method == 'POST':
            form = StudentProfileForm(request.POST, instance=student)
            if form.is_valid():
                form.save()  # Sauvegarder les modifications de l'étudiant
                return redirect('student_list')  # Rediriger vers la liste après la mise à jour
        else:
            form = StudentProfileForm(instance=student)

        return render(request, 'administrator/edit_student.html', {'form': form, 'student': student, 'logged_user': logged_user, 'current_date_time': datetime.now})

def teacher_list(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        sort_by = request.GET.get('sort_by', None)

        if sort_by == 'first_name':
            teachers = Teacher.objects.all().order_by('first_name')
        elif sort_by == 'last_name':
            teachers = Teacher.objects.all().order_by('last_name')
        else:
            teachers = Teacher.objects.all()

        return render(request, 'administrator/teacher_list.html', {'teachers': teachers, 'logged_user': logged_user, 'current_date_time': datetime.now})

def edit_teacher(request, teacher_id):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        teacher = get_object_or_404(Teacher, id=teacher_id)

        if request.method == 'POST':
            form = TeacherProfileForm(request.POST, instance=teacher)
            if form.is_valid():
                form.save()  # Sauvegarder les modifications de l'étudiant
                return redirect('teacher_list')  # Rediriger vers la liste après la mise à jour
        else:
            form = TeacherProfileForm(instance=teacher)

        return render(request, 'administrator/edit_teacher.html', {'form': form, 'teacher': teacher, 'logged_user': logged_user, 'current_date_time': datetime.now})


def edit_own_profile(request):
    logged_user = get_logged_user_from_request(request)  # Méthode que tu utilises déjà

    if not logged_user or not isinstance(logged_user, Student):
        return redirect('login')  # Redirection si pas connecté ou si ce n’est pas un étudiant

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
        form = StudentEditProfileForm(instance=student)

    return render(request, 'student/edit_profile.html', {
        'form': form,
        'student': student,
        'current_date_time': datetime.now(),
    })





def student_registration_view(request):
    user = get_logged_user_from_request(request)

    if not user or not hasattr(user, 'person_type') or user.person_type != 'etudiant':
        return redirect('login')

    registrations = user.registrations.all()

    return render(request, 'student/student_registration.html', {
        'student': user,
        'logged_user': user,
        'current_date_time': datetime.now(),
        'registrations': registrations,
    })


def student_non_passed_registrations_view(request):
    user = get_logged_user_from_request(request)

    if not user or not hasattr(user, 'person_type') or user.person_type != 'etudiant':
        return redirect('login')

    non_passed_registrations = user.registrations.filter(status='NP')

    return render(request, 'student/student_non_passed_registrations.html', {
        'student': user,
        'logged_user': user,
        'current_date_time': datetime.now(),
        'registrations': non_passed_registrations,
    })

def student_passed_registrations_view(request):
    user = get_logged_user_from_request(request)

    if not user or not hasattr(user, 'person_type') or user.person_type != 'etudiant':
        return redirect('login')

    # On récupère seulement les inscriptions avec status = 'AP' (Approuvé)
    registrations = user.registrations.select_related('academic_ue', 'academic_ue__section').filter(status='AP')

    return render(request, 'student/student_passed_registrations.html', {
        'student': user,
        'logged_user': user,
        'current_date_time': datetime.now(),
        'registrations': registrations,
    })








def student_prerequisites_view(request):
    user = get_logged_user_from_request(request)

    if not user or not hasattr(user, 'person_type') or user.person_type != 'etudiant':
        return redirect('login')

    # Récupérer toutes ses inscriptions
    registrations = user.registrations.select_related('academic_ue', 'academic_ue__section').all()

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
        'student': user,
        'logged_user': user,
        'current_date_time': datetime.now(),
        'ue_with_prerequisites': ue_with_prerequisites,
    })



def teacher_academic_ues(request):
    logged_user = get_logged_user_from_request(request)

    if not logged_user or not hasattr(logged_user, 'person_type') or logged_user.person_type != 'professeur':
        return redirect('login')  # ou une page d'erreur

    academic_ues = AcademicUE.objects.filter(teacher=logged_user)

    return render(request, 'teacher/teacher_academic_ues.html', {
        'teacher': logged_user,
        'logged_user': logged_user,
        'current_date_time': datetime.now(),
        'academic_ues': academic_ues,
    })





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
    if logged_user and logged_user.person_type == 'professeur':
        academic_ue = get_object_or_404(AcademicUE, idUE=academic_ue_id)
        registrations = Registration.objects.filter(academic_ue=academic_ue)

        if request.method == 'POST':
            for registration in registrations:
                result = request.POST.get(f'result_{registration.id}')
                status = request.POST.get(f'status_{registration.id}')
                if result:
                    registration.result = result
                if status:
                    registration.status = status
                registration.save()

            return redirect('welcomeTeacher')

        return render(request, 'teacher/encode_results.html', {
            'academic_ue': academic_ue,
            'registrations': registrations,
            'logged_user': logged_user,
        })
    else:
        return redirect('login')







def student_participation_view(request):
    user = get_logged_user_from_request(request)

    if not user or not hasattr(user, 'person_type') or user.person_type != 'etudiant':
        return redirect('login')

    # Récupérer les UEs auxquelles l'étudiant est inscrit
    academic_ues = user.academic_ues.all()

    # Si un filtre (academic_ue_id) est passé dans la requête, on filtre les participations
    selected_academic_ue = None
    participations = None

    # Vérifier si un ID d'UE est passé dans la requête GET
    if request.method == 'GET' and 'academic_ue' in request.GET and request.GET['academic_ue']:
        try:
            selected_academic_ue = AcademicUE.objects.get(id=request.GET['academic_ue'])
            participations = Participation.objects.filter(
                student=user,
                session__academicUE=selected_academic_ue
            ).select_related('session', 'session__academicUE')
        except AcademicUE.DoesNotExist:
            participations = []
    else:
        # Si aucun filtre n'est passé, afficher toutes les participations de l'étudiant
        participations = Participation.objects.filter(student=user).select_related('session', 'session__academicUE')

    return render(request, 'student/student_participation.html', {
        'student': user,
        'logged_user': user,
        'current_date_time': datetime.now(),
        'participations': participations,
        'academic_ues': academic_ues,  # Passer les UE de l'étudiant pour le filtrage
        'selected_academic_ue': selected_academic_ue  # Passer l'UE sélectionné pour la gestion de l'affichage
    })





def participations_in_ue(request, academic_ue_id):
    logged_user = get_logged_user_from_request(request)

    if not logged_user or logged_user.person_type != 'professeur':
        return redirect('login')

    academic_ue = get_object_or_404(AcademicUE, idUE=academic_ue_id, teacher=logged_user)
    sessions = academic_ue.sessions.all()
    students = Student.objects.filter(registrations__academic_ue=academic_ue).distinct()

    if request.method == 'POST':
        # Pour chaque étudiant et session, mettre à jour les participations
        for key, value in request.POST.items():
            if key.startswith('status_'):
                parts = key.split('_')  # format: status_<session_id>_<student_id>
                if len(parts) == 3:
                    _, session_id, student_id = parts
                    try:
                        session = Session.objects.get(id=session_id)
                        student = Student.objects.get(id=student_id)

                        # Filtrer les participations existantes
                        participations = Participation.objects.filter(session=session, student=student)

                        if participations.exists():
                            # Si plusieurs participations existent, vous pouvez les gérer (par exemple, en en gardant une seule)
                            # Par exemple, on peut simplement prendre la première participation
                            participation = participations.first()  # Choisir la première ou appliquer un autre critère
                        else:
                            # Créer une nouvelle participation si aucune n'existe
                            participation = Participation(session=session, student=student)

                        # Mettre à jour le statut
                        participation.status = value
                        participation.save()
                    except (Session.DoesNotExist, Student.DoesNotExist):
                        continue

        messages.success(request, "Participations mises à jour avec succès.")
        return redirect('participations_in_ue', academic_ue_id=academic_ue_id)

    session_data = []
    # Collecte des données de participation pour chaque session et chaque étudiant
    for session in sessions:
        row = {
            'session': session,
            'participations': []
        }
        for student in students:
            # Récupère ou crée une participation pour chaque session et étudiant
            participation = Participation.objects.filter(session=session, student=student).first()
            row['participations'].append({
                'student': student,
                'participation': participation  # Peut être None si la participation n'existe pas
            })
        session_data.append(row)

    return render(request, 'teacher/participations_in_ue.html', {
        'academic_ue': academic_ue,
        'session_data': session_data,
        'status_choices': Participation._meta.get_field('status').choices,
        'logged_user': logged_user,
        'current_date_time': datetime.now
    })