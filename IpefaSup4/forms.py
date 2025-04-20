from django import forms
from .models import  Educator,  Teacher, Student, Administrator, AcademicUE, UE
from django.contrib.auth.hashers import make_password, check_password
from .utils import validate_student_email
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

        # Vérifie que les mots de passe correspondent
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si un mot de passe est fourni, on le chiffre
        if self.cleaned_data.get("password"):
            instance.password = make_password(self.cleaned_data["password"])

        if commit:
            instance.save()
        return instance


class StudentForm(BaseListForm):
    class Meta:
        model = Student
        fields = '__all__'

    def save(self, commit=True):
        student = super().save(commit=False)

        # Si l'utilisateur est lié à l'étudiant, assurez-vous qu'il est correctement associé
        if 'user' in self.cleaned_data:
            user = self.cleaned_data['user']
            student.user = user  # Associe l'utilisateur à l'étudiant

        if commit:
            student.save()
            user = student.user
            if user:
                user.save()  # Sauvegarde de l'utilisateur si nécessaire

        return student


class TeacherForm(BaseListForm):
    class Meta:
        model = Teacher
        fields = '__all__'

    def save(self, commit=True):
        teacher = super().save(commit=False)

        # Assurez-vous que l'utilisateur est correctement associé à l'enseignant
        if 'user' in self.cleaned_data:
            user = self.cleaned_data['user']
            teacher.user = user  # Associe l'utilisateur à l'enseignant

        if commit:
            teacher.save()
            user = teacher.user
            if user:
                user.save()  # Sauvegarde de l'utilisateur si nécessaire

        return teacher


class AdministratorForm(BaseListForm):
    class Meta:
        model = Administrator
        fields = '__all__'

    def save(self, commit=True):
        administrator = super().save(commit=False)

        # Si l'utilisateur est lié à l'administrateur, assurez-vous qu'il est correctement associé
        if 'user' in self.cleaned_data:
            user = self.cleaned_data['user']
            administrator.user = user  # Associe l'utilisateur à l'administrateur

        if commit:
            administrator.save()
            user = administrator.user
            if user:
                user.save()  # Sauvegarde de l'utilisateur si nécessaire

        return administrator


class EducatorForm(BaseListForm):
    class Meta:
        model = Educator
        fields = '__all__'

    def save(self, commit=True):
        educator = super().save(commit=False)

        # Si un utilisateur est lié à l'éducateur, nous allons nous assurer qu'il est correctement enregistré
        if 'user' in self.cleaned_data:
            user = self.cleaned_data['user']
            educator.user = user  # Assurez-vous que l'utilisateur est bien associé à l'éducateur

        if commit:
            educator.save()
            user = educator.user
            if user:
                user.save()  # Sauvegarde de l'utilisateur si nécessaire

        return educator


class AddAcademicUEForm(forms.ModelForm):

    class Meta:
        model = AcademicUE
        fields = '__all__'  # Pas besoin de `exclude = {}` si on utilise `fields = '__all__'`


class AddUEForm(forms.ModelForm):


    class Meta:
        model = UE
        fields = '__all__'





class StudentProfileForm(BaseListForm):#liste des étudiants


    class Meta:
        model = Student
        fields = '__all__'  # Corriger la syntaxe



class TeacherProfileForm(BaseListForm):


    class Meta:
        model = Teacher
        fields = '__all__'  # Corriger la syntaxe
