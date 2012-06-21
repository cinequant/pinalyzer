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
    
    def updateScore(self,res,diff):
        self.match+=1
        f=400.0 # Coef pour étendre la plage de valeur
        p=1.0/(1.0+pow(10.0,-float(diff)/f))
        k=10
        self.score+=int(k*(float(res)-p))
        self.save()
        
    def __str__(self):
        return str(self.pin_id)
    
    def __unicode__(self):
        return unicode(self.pin_id)
    
class CategoryModel(models.Model):
    category_id=models.CharField(max_length=200,unique=True,default='')
    category_name=models.CharField(max_length=200,default='')
    
    

    
    