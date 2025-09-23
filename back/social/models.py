from io import BytesIO
from uuid import uuid4

from django.contrib.auth import models as models2
from django.core.files import File
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from unidecode import unidecode

from trade.models import Transaction


class Promotion(models.Model):
    year = models.IntegerField()
    name = models.CharField(max_length=50, default="default")
    nickname = models.CharField(max_length=3, default="000")

    def __str__(self):
        return self.nickname


class Nationality(models.Model):
    nationality = models.CharField(max_length=30, default="Française")
    short_nationality = models.CharField(max_length=3, default="FR")

    def __str__(self):
        return self.short_nationality


class Role(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(models2.User(), on_delete=models.PROTECT)
    promo = models.ForeignKey("Promotion", on_delete=models.SET_NULL, null=True)

    class Department(models.TextChoices):
        IMI = "IMI", _("Ingénierie mathématique et informatique")
        GCC = "GCC", _("Génie civil et construction")
        GMM = "GMM", _("Génie mécanique et matériaux")
        SEGF = "SEGF", _("Sciences économiques, gestion, finance")
        VET = "VET", _("Ville, environnement, transport")
        GI = "GI", _("Génie industriel")
        A1 = "1A", _("Première année")

    department = models.CharField(
        max_length=4, choices=Department.choices, default=Department.A1
    )

    class Gender(models.TextChoices):
        F = "Femme"
        H = "Homme"
        A = "Autre"

    gender = models.CharField(max_length=5, choices=Gender.choices, default=Gender.A)

    class Origin(models.TextChoices):
        CC = "Concours Commun"
        BCPST = "BCPST"
        AST = "Admission Sur Titre"
        DD = "Double Diplôme"
        ETR = "Université étrangère"

    origin = models.CharField(max_length=20, choices=Origin.choices, default=Origin.CC)

    phone_regex = RegexValidator(
        regex=r"^\+?\d{9,16}$",
        message=(
            "Le numéro doit être entré au format: '+999999999'. Jusqu'à 16 chiffres"
            " sont autorisés."
        ),
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, null=True, blank=True
    )  # validators should be a list
    birthdate = models.DateField(max_length=12, null=True, blank=True)
    biography = models.TextField(max_length=300, null=True, blank=True)
    public_key = models.TextField(max_length=100, null=True)
    picture = models.ImageField(upload_to="pictures/", null=True, blank=True)
    nationality = models.ForeignKey(
        "Nationality", on_delete=models.SET_NULL, null=True, blank=True
    )
    first_connection = models.BooleanField(default=True)
    is_validated = models.BooleanField(default=True)
    is_moderator = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.picture:
            self.picture = compress_image(self.picture, 50, self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    def balance_in_cents(self, club=None):
        if club is None:
            transactions = Transaction.objects.filter(student=self)
        else:
            transactions = Transaction.objects.filter(student=self).filter(
                good__club=club
            )

        balance = 0
        for transaction in transactions:
            balance += transaction.balance_change_for_student()
        return balance

    def balance_in_euros(self, club=None):
        return self.balance_in_cents(club) / 100


class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=50, default="Club")
    nickname = models.CharField(max_length=50, default="", null=True, blank=True)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    background_picture = models.ImageField(
        upload_to="background_pictures/", null=True, blank=True
    )
    description = models.TextField()
    active = models.BooleanField()
    has_fee = models.BooleanField()
    category = models.ManyToManyField(
        Category,
        related_name="category",
        blank=True,
    )
    members = models.ManyToManyField(
        Student,
        through="Membership",
        related_name="clubs",
        blank=True,
    )

    class Label(models.TextChoices):
        ASSO = "Association"
        CLUB = "Club"
        LISTE = "Liste"
        POLE = "Pôle"

    label = models.CharField(max_length=20, choices=Label.choices, default=Label.CLUB)

    def save(self, *args, **kwargs):
        if self.logo:
            self.logo = compress_image(self.logo, 30, unidecode(self.name))
        if self.background_picture:
            self.background_picture = compress_image(
                self.background_picture, 50, unidecode(self.name)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def is_member(self, student_id):
        for student in self.members.all():
            if student.id == student_id:
                return True
        return False

    def is_admin(self, student_id):
        membership = Membership.objects.filter(student__id=student_id, club=self)
        if len(membership) > 0 and membership[0].is_admin:
            return True
        return False

    def balance_in_cents(self):
        transactions = Transaction.objects.filter(good__club=self)
        balance = 0
        for transaction in transactions:
            balance += transaction.balance_change_for_club()
        return balance

    def balance_in_euros(self):
        return self.balance_in_cents() / 100

    def getMembers(self):
        return self.members.filter(membership__is_old=False)


class Membership(models.Model):
    is_admin = models.BooleanField()
    is_old = models.BooleanField(default=False)
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.club.name + " : " + self.student.user.username


class ClubRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    content = models.TextField()

    def __str__(self):
        return self.student.user.username + " : " + self.name


class NotificationToken(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    token = models.CharField(max_length=200)

    def __str__(self):
        return self.student.user.username + " : " + self.token


def compress_image(image, quality, name):
    im = Image.open(image)
    im = im.convert("RGB")
    im_io = BytesIO()
    im.save(im_io, "JPEG", quality=quality, optimize=True)
    new_image = File(im_io, name=name + "_" + uuid4().hex + ".jpg")
    return new_image


class Message(models.Model):
    channel = models.ForeignKey("Channel", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    author = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    club = models.ForeignKey(
        "social.Club", on_delete=models.SET_NULL, null=True, blank=True
    )
    content = models.TextField()

    def __str__(self):
        author = [self.author, self.club][bool(self.club)]
        return f"Message from {author}: '{self.content}'"


class Channel(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateTimeField()
    creator = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    club = models.ForeignKey(
        "social.Club", on_delete=models.SET_NULL, null=True, blank=True
    )
    members = models.ManyToManyField("social.Student", related_name="channels")
    admins = models.ManyToManyField("social.Student", related_name="channels_admin")
    encrypted_keys = models.ManyToManyField("social.ChannelEncryptedKey")


class ChannelEncryptedKey(models.Model):
    key = models.TextField(max_length=100, null=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="encrypted_channel_keys",
        null=True,
    )
