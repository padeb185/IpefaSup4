import re
from django.core.exceptions import ValidationError
from IpefaSup4.models import Student, Teacher, Educator, Administrator


def get_logged_user_from_request(request):
    """Fonction pour récupérer l'utilisateur connecté à partir de la session"""
    user_id = request.session.get('logged_user_id')
    if not user_id:
        return None

    try:
        person_type = request.session.get('person_type')

        if person_type == 'etudiant':
            return Student.objects.get(id=user_id)

        elif person_type == 'professeur':
            return Teacher.objects.get(id=user_id)

        elif person_type == 'administrateur':
            # L'utilisateur est un administrateur → on le récupère directement
            return Administrator.objects.get(id=user_id)

        elif person_type == 'educateur':
            # Vérifier si c'est un administrateur déguisé en éducateur
            educator = Educator.objects.get(id=user_id)
            try:
                return educator.administrator  # Remonte à l'administrateur
            except Administrator.DoesNotExist:
                return educator

        else:
            return None

    except (Student.DoesNotExist, Teacher.DoesNotExist, Educator.DoesNotExist, Administrator.DoesNotExist):
        return None

