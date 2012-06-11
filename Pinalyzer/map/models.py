# -*- coding: utf-8 -*-
from django.db import models

class UserModel(models.Model):
    user_id = models.CharField(max_length=200, primary_key=True)
    address = models.CharField(max_length=200) #Un user_id peut avoir qu'une address (à voir)
    
class LocationModel(models.Model):
    address = models.CharField(max_length=200, primary_key=True)   
    lat=models.FloatField()
    lng=models.FloatField()