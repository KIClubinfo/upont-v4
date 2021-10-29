from django.db import models
from django.contrib.auth import models as models2
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class Promotion(models.Model):
    year = models.IntegerField()
    name = models.CharField(max_length=50, default='default')

class Nationality(models.Model):
    nationality = models.CharField(max_length=30, default='Française')
    short_nationality = models.CharField(max_length=3, default='FR')

class Role(models.Model):
    name = models.CharField(max_length=30, default='Membre')

class Membership(models.Model):
    is_admin = models.BooleanField()
    #student = models.ForeignKey('Student', on_delete=models.CASCADE)
    #club = models.ForeignKey('Club', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)

class Student(models.Model):
    user = models.OneToOneField(models2.User(), on_delete=models.CASCADE, null=True)
    promo = models.ForeignKey('Promotion', on_delete=models.CASCADE, null=True)

    class Department(models.TextChoices):
        IMI = 'Ingénierie mathématique et informatique'
        GCC = 'Génie civil et construction'
        GMM = 'Génie mécanique et matériaux'
        SEGF = 'Sciences économiques, gestion, finance'
        VET = 'Ville, environnement, transport'
        GI = 'Génie industriel'
        A1 = 'Première année'
    department = models.CharField(
        max_length=50,
        choices=Department.choices,
        default = Department.A1
    )
    class ShortDepartment(models.TextChoices):
        IMI = 'IMI'
        GCC = 'GCC'
        GMM = 'GMM'
        SEGF = 'SEGF'
        VET = 'VET'
        GI = 'GI'
        A1 = '1A'
    short_department = models.CharField(
        max_length=4,
        choices=ShortDepartment.choices,
        default = Department.A1
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
    picture = models.ImageField(upload_to='pictures', null=True, blank=True)
    nationality = models.ForeignKey('Nationality', on_delete=models.CASCADE, null=True)
    clubs = models.ManyToManyField(Membership())

class Category(models.Model):
    type = models.CharField(max_length=30)

class Club(models.Model):
    name = models.CharField(max_length=50, default='Club')
    nickname = models.CharField(max_length=10, default='Club')
    logo = models.ImageField(upload_to='logos')
    description = models.TextField()
    active = models.BooleanField()
    has_fee = models.BooleanField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    members = models.ManyToManyField(Membership())