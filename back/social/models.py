from django.db import models
from django.contrib.auth import models as models2
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class Promotion(models.Model):
    year = models.IntegerField()

class Student(models.Model):
    user = models2.User()
    promo = Promotion()

    class Department(models.TextChoices):
        IMI = 'IMI', _('Ingénierie mathématique et informatique')
        GCC = 'GCC', _('Génie civil et construction')
        GMM = 'GMM', _('Génie mécanique et matériaux')
        SEGF = 'SEGF', _('Sciences économiques, gestion, finance')
        VET = 'VET', _('Ville, environnement, transport')
        GI = 'GI',_('Génie industriel')
        A1 = '1A',_('Première année')
    department = models.CharField(
        max_length=4,
        choices=Department.choices,
    )

    class Gender(models.TextChoices):
        F = 'Femme'
        H = 'Homme'
        A = 'Autre'
    gender = models.CharField(
        max_length=5,
        choices=Gender.choices,
        default = Gender.A
    )

    class Origin(models.TextChoices):
        CC = 'Concours Commun'
    origin = models.CharField(
        max_length=20,
        choices=Origin.choices,
        default = Origin.CC
    )

    phone_regex = RegexValidator(regex=r'^\+?\d{9,16}$', message="Le numéro doit être entré au format: '+999999999'. Jusqu'à 16 chiffres sont autorisés.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
