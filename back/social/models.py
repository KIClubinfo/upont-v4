from django.db import models
from django.contrib.auth import models as models2
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class Promotion(models.Model):
    year = models.IntegerField()
    name = models.CharField(max_length=50, default='default')
    nickname = models.CharField(max_length=3, default='000')
    def __str__(self):
        return self.nickname


class Nationality(models.Model):
    nationality = models.CharField(max_length=30, default='Française')
    short_nationality = models.CharField(max_length=3, default='FR')
    def __str__(self):
        return self.short_nationality


class Role(models.Model):
    name = models.CharField(max_length=30, default='Membre')
    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(models2.User(), on_delete=models.CASCADE, null=True)
    promo = models.ForeignKey('Promotion', on_delete=models.CASCADE, null=True)

    class Department(models.TextChoices):
        IMI = 'IMI', _('Ingénierie mathématique et informatique')
        GCC = 'GCC', _('Génie civil et construction')
        GMM = 'GMM', _('Génie mécanique et matériaux')
        SEGF = 'SEGF', _('Sciences économiques, gestion, finance')
        VET = 'VET', _('Ville, environnement, transport')
        GI = 'GI', _('Génie industriel')
        A1 = '1A', _('Première année')
    department = models.CharField(
        max_length=4,
        choices=Department.choices,
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
    def __str__(self):
        return self.user.username

    def clubs(self):
        values = Membership.objects.filter(student=self).values_list('club__name', flat=True)
        text = ""
        for name in values:
            text = text + name + ", "
        if text!="":
            return text[:-2]
    clubs.empty_value_display = 'Aucun club'


class Category(models.Model):
    type = models.CharField(max_length=30)
    def __str__(self):
        return self.type


class Club(models.Model):
    name = models.CharField(max_length=50, default='Club')
    nickname = models.CharField(max_length=10, default='Club')
    logo = models.ImageField(upload_to='logos', null=True, blank=True)
    description = models.TextField()
    active = models.BooleanField()
    has_fee = models.BooleanField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    def membres(self):
        values = Membership.objects.filter(club=self).values_list('student__user__username', flat=True)
        text = ""
        for name in values:
            text = text + name + ", "
        if text!="":
            return text[:-2]
    membres.empty_value_display = 'Aucun membre'


class Membership(models.Model):
    is_admin = models.BooleanField()
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, null=True)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    def __str__(self):
        return self.club.name + ' : ' + self.student.user.username