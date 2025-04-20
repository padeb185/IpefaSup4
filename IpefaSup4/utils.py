import re

from django.core.exceptions import ValidationError

from IpefaSup3.models import Student, Teacher, Educator, Administrator


def get_logged_user_from_request(request):
    """Fonction pour récupérer l'utilisateur connecté à partir de la session"""
    user_id = request.session.get('logged_user_id')
    if user_id:
        try:
            # Récupérer l'utilisateur selon le type de personne dans la session
            person_type = request.session.get('person_type')
            if person_type == 'etudiant':
                return Student.objects.get(id=user_id)
            elif person_type == 'professeur':
                return Teacher.objects.get(id=user_id)
            elif person_type == 'educateur':
                return Educator.objects.get(id=user_id)
            elif person_type == 'administrateur':
                return Administrator.objects.get(id=user_id)
            else:
                return None  # Si le type est inconnu
        except (Student.DoesNotExist, Teacher.DoesNotExist, Educator.DoesNotExist, Administrator.DoesNotExist):
            return None
    return None


def validate_student_email(email):
    pattern = r"^[a-z]+\.[a-z]+@(student\.)?efpl\.be$"
    if not re.match(pattern, email, re.IGNORECASE):
        raise ValidationError("L'adresse email doit être du type nom.prenom@student.efpl.be ou nom.prenom@efpl.be")