from django.db import models

# Create your models here.

# Place in an apartment (ex: a bedrooom)
class Room(models.Model):
    occupant = models.ForeignKey('Student', on_delete=models.CASCADE) # The occupant of the place
    not_from_ponts = models.BooleanField() # If the Studen is not from Ponts
    rent_without_charges = models.IntegerField() # The rent without charges (in cents)
    charges = models.IntegerField() # The charges (in cents)
    description = models.TextField() # A description of the place
    illustration = models.ImageField(upload_to='room_illustrations') # An illustration of the place

# Apartments
class Apartment(models.Model):
    name = models.CharField(max_length=50) # The name of the apartment
    rooms = models.ManyToManyField(Room, blank=True) # The rooms of the apartment
    description = models.TextField() # A description of the apartment
    illustration = models.ImageField(upload_to='apartment_illustrations') # An illustration of the apartment
    localisation = models.CharField(max_length=50) # The localisation of the apartment
    adress = models.CharField(max_length=200) # The adress of the apartment
