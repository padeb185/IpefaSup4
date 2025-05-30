from django import forms
from .models import Educator, Teacher, Student, Administrator, AcademicUE, UE, Registration, Participation, Session, \
    Section, validate_student_email
from django.contrib.auth.hashers import make_password, check_password

from django import forms


class LoginForm(forms.Form):
    matricule = forms.CharField(label='Matricule', required=False)
    email = forms.EmailField(label="Courriel", required=False, validators=[validate_student_email])
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        matricule = cleaned_data.get("matricule")

        # Debug : Affiche les informations reçues
        print(f"Email: {email}, Matricule: {matricule}, Password: {password}")

        if email and password:
            # Authentification par email pour les étudiants
            try:
                student = Student.objects.get(studentMail=email)
                if not check_password(password, student.password):
                    raise forms.ValidationError("Adresse mail ou mot de passe incorrect")
            except Student.DoesNotExist:
                raise forms.ValidationError("Adresse mail ou mot de passe incorrect")

        elif matricule and password:
            user = None

            # Cherche d'abord dans la table Teacher
            try:
                user = Teacher.objects.get(matricule=matricule.strip())
            except Teacher.DoesNotExist:
                pass

            # Si pas trouvé dans Teacher, cherche dans Educator
            if not user:
                try:
                    user = Educator.objects.get(matricule=matricule.strip())
                except Educator.DoesNotExist:
                    raise forms.ValidationError("Matricule ou mot de passe incorrect")

            # Vérification du mot de passe
            if user and not check_password(password, user.password):
                raise forms.ValidationError("Matricule ou mot de passe incorrect")

        else:
            raise forms.ValidationError("Veuillez entrer un email ou un matricule avec le mot de passe.")

        return cleaned_data







class BaseListForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Mot de passe')
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label='Confirmer le mot de passe')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get("password"):
            instance.password = make_password(self.cleaned_data["password"])

        if commit:
            instance.save()
        return instance



class StudentForm(BaseListForm):
    class Meta:
        model = Student
        exclude = ['academic_ues', 'sessions']
        widgets = {
            'studentMail': forms.EmailInput(attrs={'id': 'studentMail'})
        }




class TeacherForm(BaseListForm):
    class Meta:
        model = Teacher
        fields = '__all__'
        widgets = {
            'matricule': forms.TextInput(attrs={'id': 'matricule-teacher', 'class': 'form-control'}),
            'employee_email': forms.EmailInput(attrs={'id': 'employee_email-teacher', 'class': 'form-control'}),
        }

class AdministratorForm(BaseListForm):
    class Meta:
        model = Administrator
        fields = '__all__'
        widgets = {
            'matricule': forms.TextInput(attrs={'id': 'matricule-administrator', 'class': 'form-control'}),
            'employee_email': forms.EmailInput(attrs={'id': 'employee_email-administrator', 'class': 'form-control'}),
        }

class EducatorForm(BaseListForm):
    class Meta:
        model = Educator
        fields = '__all__'
        widgets = {
            'matricule': forms.TextInput(attrs={'id': 'matricule-educator', 'class': 'form-control'}),
            'employee_email': forms.EmailInput(attrs={'id': 'employee_email-educator', 'class': 'form-control'}),
        }

class AddAcademicUEForm(forms.ModelForm):
    class Meta:
        model = AcademicUE
        exclude = {'educator'}



class AddUEForm(forms.ModelForm):
    class Meta:
        model = UE
        fields = '__all__'


class AddRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = '__all__'


class AddParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = '__all__'


class AddSessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = '__all__'


class AddSectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'
        widgets = {
            'wording': forms.TextInput(attrs={'id': 'wording', 'class': 'form-control'}),
        }



class StudentProfileForm(BaseListForm):#liste des étudiants
    class Meta:
        model = Student
        exclude =  ['academic_ues', 'sessions'] # Corriger la syntaxe



class TeacherProfileForm(BaseListForm):
    class Meta:
        model = Teacher
        fields = '__all__'  # Corriger la syntaxe


class StudentEditProfileForm(BaseListForm):
    class Meta:
        model = Student
        exclude = ['academic_ues', 'sessions', 'ue']


from django import forms
from .models import Registration

class RegistrationApprovalForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [ 'result', 'status', 'approved']
        widgets = {
            'student': forms.TextInput(attrs={'readonly': 'readonly'}),
            'academic_ue': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si tu veux que ces champs restent readonly, on remplace les champs ModelChoiceField par des champs TextInput affichant un texte
        # Donc ici, on remplace les champs par des champs CharField affichant le texte au lieu de ModelChoiceField

        # Pour afficher le nom complet de l'étudiant dans un champ readonly
        if self.instance and self.instance.pk:
            self.fields['student'] = forms.CharField(
                initial=f"{self.instance.student.first_name} {self.instance.student.last_name}",
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )
            # Afficher le wording de l'AcademicUE dans un champ readonly
            self.fields['academic_ue'] = forms.CharField(
                initial=self.instance.academic_ue.wording,
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )
