# -*- coding: utf-8 -*-
from django.db import models

class UserModel(models.Model):
    user_id = models.CharField(max_length=200, unique=True)
    nb_followers=models.IntegerField(default=0)
    nb_pins=models.IntegerField(default=0)
    score=models.FloatField(default=0)
    
    class Meta:
        app_label = 'map'
        
class LocationModel(models.Model):
    address = models.CharField(max_length=200, primary_key=True)   
    lat=models.FloatField()
    lng=models.FloatField()
    class Meta:
        app_label = 'map'
    
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
    class Meta:
        app_label = 'map'
        
    def __str__(self):
        return str(self.pin_id)
    
    def __unicode__(self):
        return unicode(self.pin_id)
    
class CategoryModel(models.Model):
    category_id=models.CharField(max_length=200,unique=True,default='')
    category_name=models.CharField(max_length=200,default='')
    class Meta:
        app_label = 'map'
    
    

    
    
