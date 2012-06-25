# -*- coding: utf-8 -*-
from django.db import models

class UserModel(models.Model):
    user_id = models.CharField(max_length=200, primary_key=True)
    address = models.CharField(max_length=200)
    
class LocationModel(models.Model):
    address = models.CharField(max_length=200, primary_key=True)   
    lat=models.FloatField()
    lng=models.FloatField()
    
class PinModel(models.Model):
    id = models.AutoField(primary_key=True)
    url=models.URLField(unique=True,max_length=200)
    score=models.IntegerField(default=0)
    match=models.IntegerField(default=0)
    pin_id=models.CharField(unique=True,max_length=200)
    pinner_id=models.CharField(max_length=200)
    pinner_name=board_id=models.CharField(max_length=200)
    board_id=models.CharField(max_length=200)
    board_name=models.CharField(max_length=200)
    category=models.ForeignKey('CategoryModel')
    width=models.IntegerField()
    height=models.IntegerField()
        
    def __str__(self):
        return str(self.pin_id)
    
    def __unicode__(self):
        return unicode(self.pin_id)
    
class CategoryModel(models.Model):
    category_id=models.CharField(max_length=200,unique=True,default='')
    category_name=models.CharField(max_length=200,default='')
    
class ScoringModel(models.Model):
    user_id = models.ForeignKey('UserModel',unique=True)
    nb_pin=models.IntegerField(default=0)
    nb_follower=models.IntegerField(default=0)
    nb_like=models.IntegerField(default=0)
    nb_repin=models.IntegerField(default=0)
    nb_comment=models.IntegerField(default=0)
    sampled_pin=models.IntegerField(default=0)
    
    

    
    
