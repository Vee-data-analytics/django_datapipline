from django.db import models
from allauth.account.signals import user_logged_in
from django.urls import reverse
from users.models import Programer
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
Class Customer_BOMS(models.Model):
    user = ForeignKey(Programer, on_delete=models.SET_NULL, null=True)
    CATEGORIES = {
    'LANDIS': 'Landis & Gyr',
    'CARTRACK': ' CarTrack ',
    'KAON': 'ETV | Platco',
    'DME': 'Digital matter',
    }
    CAT_CHOICES = [(code, lables) for code, lables in CATEGORIES.items() ]
    name = models.TextField(choices=CAT_CHOICES, max_length = 50,null =True)
    product = models.TextField(max_length=250, null=True, )
    
    date_of_upload = models.DateTimeField(default=time_zone.now, null=True)