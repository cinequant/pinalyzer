# -*- coding: utf-8 -*-
from django.db import models
import math, time

class UserModel(models.Model):
    user_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    photo_url = models.URLField(max_length=200)
    location = models.CharField(max_length=200, null=True)
    
    def get_stat_historic(self):
        return self.userstatmodel_set.all().order_by('date')
    
    def get_stat_evolution(self, prev=1):
        stat_list=self.get_stat_historic()
        last_stat=stat_list[-1]
        prev_stat=stat_list[-1-prev]
        return prev_stat, last_stat
    
    def latest_stat(self):
        h=self.get_stat_historic()
        return h[len(h)-1]
    
    def get_history(self):
        h=self.get_stat_historic()
        res=[]
        for stat in h:
            epoch= time.mktime(stat.date.timetuple())*1000
            print epoch
            score=stat.score()
            res.append([epoch,score])
        return res
    
    @classmethod
    def get_distribution(cls):
        rep=[0]*10
        user_q=cls.objects.all()
        for u in user_q:
            s=u.latest_stat().score()
            i=int(s)/10
            rep[i]+=1
            print 'hey'
        return [int((float(x)/float(len(user_q)))*1000)/10.0 for x in rep]
        
    
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
        
        
class UserStatModel(models.Model):
    date=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey('UserModel') 
    nb_board=models.IntegerField(default=0)
    nb_pin=models.IntegerField(default=0)
    nb_liked=models.IntegerField(default=0)
    nb_followers=models.IntegerField(default=0)
    nb_following=models.IntegerField(default=0)
    nb_repin=models.IntegerField(default=0) # estimé
    nb_comment=models.IntegerField(default=0) # estimé
    nb_like=models.IntegerField(default=0) # estimé
    
    def score(self):
        # Poids
        w_followers=45.0
        w_following=3.0
        w_pin=5.0
        w_like=7.0
        w_comment=20
        w_repin=20
        
        
        # Valeurs moyennes
        e_followers=500
        e_following=100
        e_pin=500
        e_like=1000
        e_comment=200
        e_repin=1500
        
        #Notes par rapport à une moyenne : <1 si en dessous à la moyenne, >1 si au dessus de la moyenne, vers 1 si vers la moyenne
        r_followers=float(self.nb_followers)/float(e_followers)
        r_following=float(self.nb_following)/float(e_following)
        r_pin=float(self.nb_pin)/float(e_pin)
        r_like=float(self.nb_like)/float(e_like)
        r_comment=float(self.nb_comment)/float(e_comment)
        r_repin=float(self.nb_repin)/float(e_repin)
        
        
        """
        print 'r_followers %f'% r_followers,
        print 'r_following %f'% r_following,
        print 'r_pin %f'% r_pin,
        print 'r_like %f'% r_like,
        print 'r_comment %f'% r_comment,
        print 'r_repin %f'% r_repin,
        """
               
        c=60
        d=3

        r_followers=math.log(1+c*r_followers)
        r_following=math.log(1+c*r_following)
        r_pin=math.log(1+c*r_pin)
        r_like=math.log(1+c*r_like)
        r_comment=math.log(1+c*r_comment)
        r_repin=math.log(1+c*r_repin)
        
       

        res=w_followers*r_followers+ w_following*r_following + w_pin*r_pin+w_like*r_like+w_comment*r_comment+w_repin*r_repin
        res_moy=(w_followers+w_following+w_pin+w_like+w_comment+w_repin)*math.log(c/d+1)
        
        # (1-e(-a*res_moy))*100=50
        # a=-ln(1/2)/res_moy
        # a=math.log(2)/res_moy

        
        #score=(1.0-math.exp(-a*res))*100
        score=100*res/(res_moy+res)
        
        """
        
        c=2 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        r_followers=w_followers*r_followers/(r_followers+math.log(c+1))
        r_following=w_following*r_following/(r_following+math.log(c+1))
        r_pin=w_pin*r_pin/(r_pin+math.log(c+1))
        r_like=w_like*r_like/(r_like+math.log(c+1))
        r_comment=w_comment*r_comment/(r_comment+math.log(c+1))
        r_repin=w_repin*r_repin/(r_repin+math.log(c+1))
        
        score=r_followers+r_following+r_pin+r_like+r_repin+r_comment
        """
        
        return score
    
    class Meta:
        app_label = 'map'
    
    
    

    
    
