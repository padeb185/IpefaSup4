from datetime import datetime
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .forms import LoginForm, StudentForm, TeacherForm, AdministratorForm, AddAcademicUEForm, AddUEForm, \
    StudentProfileForm, EducatorForm, TeacherProfileForm
from .models import Educator, Student, Teacher, \
     Administrator
from django.shortcuts import render
from .utils import get_logged_user_from_request


def welcome(request):
    logged_user = get_logged_user_from_request(request)

    if logged_user:
        if logged_user.person_type == 'etudiant':
            return render(request, 'student/welcomeStudent.html', {'logged_user': logged_user})
        elif logged_user.person_type == 'professeur':
            return render(request, 'teacher/welcomeTeacher.html', {'logged_user': logged_user})
        elif logged_user.person_type == 'educateur':
            return render(request, 'educator/welcomeEducator.html', {'logged_user': logged_user})
        elif logged_user.person_type == 'administrateur':
            return render(request, 'administrator/welcomeAdmin.html', {'logged_user': logged_user})
        else:
            # Si le type est inconnu, redirection vers la page de connexion
            return redirect(reverse('login'))
    else:
        # Si aucun utilisateur connecté, redirection vers la page de connexion
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


from django.shortcuts import render, redirect
from .forms import StudentForm, TeacherForm, EducatorForm, AdministratorForm


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
            return redirect('/login')  # Redirigez après la création du compte
        elif profile_type == 'Teacher' and teacherForm.is_valid():
            teacherForm.save()
            return redirect('/login')
        elif profile_type == 'Educator' and educatorForm.is_valid():
            educatorForm.save()
            return redirect('/login')
        elif profile_type == 'Administrator' and administratorForm.is_valid():
            administratorForm.save()
            return redirect('/login')

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
    if not logged_user:
        return redirect('login')  # Ou une autre redirection en cas d'absence d'utilisateur connecté

    if request.method == 'POST':
        form = AddAcademicUEForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Remplace par la page vers laquelle tu veux rediriger après ajout
    else:
        form = AddAcademicUEForm()

    return render(request, 'administrator/add_academic_ue.html', {
        'form': form,
        'logged_user': logged_user,
        'current_date_time': datetime.now(),
    })


def add_ue_views(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if request.method == 'POST':
            form = AddUEForm(request.POST)
            if form.is_valid():
                form.save()  # Sauvegarde les données si le formulaire est valide
                # Rediriger ou renvoyer une réponse après soumission
        else:
            form = AddUEForm()  # Crée une nouvelle instance du formulaire

        return render(request, 'administrator/add_ue.html',
                      {'form': form, 'logged_user': logged_user, 'current_date_time': datetime.now})




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
