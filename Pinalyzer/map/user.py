# -*- coding: utf-8 -*-
from django.db import  IntegrityError
from django.utils.simplejson import loads, dumps
from models import UserModel, LocationModel, UserStatModel
from userheader import UserHeader
from pinlistpage import PinListPage, NoPinsError

import urllib3
import re
import string, random
import datetime
import fun
from threading import Thread, Lock

http = urllib3.PoolManager()

# Calculate from an adress, the corresponding geographic coordinates ( a (lat,lng) couple ), using geocoding service ( google map api).
def addressToLatLng(address):
    adr=string.replace(address, ' ', '+') 
    r=http.request('GET','https://maps.googleapis.com/maps/api/geocode/json?address='+adr+'&sensor=false')
    json_output=r.data
    output=loads(json_output)
    
    if output['status'] != "OK":
        raise Exception('status ='+output['status'])
    
    return (output['results'][0]['geometry']['location']['lat'],output['results'][0]['geometry']['location']['lng'])


class User:
    
    @staticmethod
    def getUserIdList(nb_page=10):
        res=[]
        for p in range(1,nb_page+1):
            r=http.request('GET','http://pinterest.com/popular/?lazy=1&page='+str(p))
            l=[match.group('id') for match in re.finditer(User.re_name,r.data) if match.group('id')[:3] !='all' ]
            res.extend(list(set(l)))
        return res
    
    @staticmethod
    def fetchPopularUsers(nb_page=10):
        user_id_list=User.getUserIdList(nb_page)
        total=0
        not_fetched=0
        for user_id in user_id_list:
            total+=1
            u=User(user_id)
            try:
                u.fetchUser()
                u.fetchScoring()
                u.saveDB()
            except Exception:
                not_fetched+=1
        return not_fetched,total
                
                
    @staticmethod
    def fetchLatestStats():
        total = 0
        not_fetched = 0
        for user in UserModel.objects.all():
            try:
                d = datetime.datetime.now()
                stat = user.userstatmodel_set.get(date__year=d.year, date__month=d.month, date__day=d.day)
            except UserStatModel.DoesNotExist:
                total += 1
                u = User(user.user_id)
                try:
                    u.fetchUser()
                    u.fetchScoring()
                    u.saveDB()
                except Exception:
                    not_fetched += 1
        return not_fetched,total
    
    @staticmethod
    def modelToUser(u_model):
        u=User(u_model.user_id)
        u.name=u_model.name
        u.photo_url=u_model.photo_url
        u.location=u_model.location
        return u
                    
        
    def __init__(self,user_id,location=None, name=None, photo_url=None,nb_followers=None,nb_following=None):
        self.id=user_id # User id in pinterest
        self.name=name # User name
        self.photo_url=photo_url 
        self.followers=None
        self.following=None
        self.nb_followers=nb_followers
        self.nb_following=nb_following
        self.nb_pin=None
        self.nb_repin=None
        self.location=location #User location , ex: "Paris,France"
        self.lat=None # Latitude
        self.lng=None # Longitude
    def __str__(self):
        return '{self.id},{self.name}'.format(self=self)
    
    def __eq__(self,o):
        return self.id==o.id
    
    def __hash__(self):
        return self.id
        
    def url(self):
        return 'http://www.pinterest.com/{0}'.format(self.id)
        
    def fetchUser(self,header_info=None):
        if header_info==None:
            header_info=UserHeader(self.id)
            header_info.fetch()
        self.name=header_info.name
        self.location=header_info.location
        self.photo_url=header_info.photo_url
        self.nb_board=header_info.nb_board
        self.nb_pin=header_info.nb_pin
        self.nb_like=header_info.nb_like
        self.nb_followers=header_info.nb_followers
        self.nb_following=header_info.nb_following     
            
    def fetchScoring(self):
        if not self.nb_pin:
            self.fetchUser()
        pins_info=PinListPage('{0}/pins/?page='.format(self.url()), self.id)
        nb_pages=self.nb_pin/50 + (self.nb_pin%50 !=0)
        pins_info.fetch(nb_pages)
        pins_info.calcScoringInfo(self.nb_pin)
        self.nb_liked=pins_info.nb_liked
        self.nb_comment=pins_info.nb_comment
        self.nb_repin=pins_info.nb_repin
        
    def fetchFollowers(self, nb_page):
        from followpage import FollowPage
        f_page=FollowPage(self.id,'followers')
        f_page.fetch(nb_page)
        self.fetchUser(f_page.user_info)
        self.saveDB()
        self.followers=f_page.follow_list
        
    def fetchFollowing(self, nb_page):
        from followpage import FollowPage
        f_page=FollowPage(self.id,'following')
        f_page.fetch(nb_page)
        self.fetchUser(f_page.user_info)
        self.saveDB()
        self.following=f_page.follow_list
        
    def getBestFollowers(self,nb, key=lambda u: u.nb_followers):
        if self.followers==None:
            self.fetchFollowers(1)
        self.followers.sort(key=key)
        nb=min(nb,len(self.followers))
        return self.followers[-nb:]
    
    def getBestFollowing(self,nb, key=lambda u: u.nb_followers):
        if self.following==None:
            self.fetchFollowing(1)
        self.following.sort(key=key)
        nb=min(nb,len(self.following))
        return self.following[-nb:]
    
    def getAlikes(self):
        best_following=self.getBestFollowing(10)
        if best_following:
            best_following=random.sample(best_following,1)
            alikes=[]
            thread_list=[]
            lock=Lock()
            for u in best_following:
                def task(user):
                    user.fetchFollowers(1)
                    best_followers=user.followers
                    lock.acquire()
                    alikes.extend(best_followers)
                    lock.release()
                t=Thread(target=task,args=(u,))
                thread_list.append(t)      
            for t in thread_list:
                t.start()
            for t in thread_list:
                t.join()
            alikes=fun.sort_by_freq(alikes)
            alikes=filter(lambda x:x.id!=self.id, alikes)
            return alikes
        else:
            return []
    
    def getToFollow(self,alikes=None):
        if not alikes:
            alikes=self.getAlikes()
        if alikes:
            alike=alikes[-1]
            to_follow=[]
            cpt=0
            i=0
            l=alike.getBestFollowing(20)
            while cpt<len(l) and i<len(l):
                if l[i] not in self.following and l[i] not in to_follow:
                    to_follow.append(l[i])
                    cpt+=1
                i+=1    
            return to_follow
        else:
            return []
    
    def getToRepin(self,nb=10):
        nb_user=2 
        to_follow=self.getToFollow()[-10:]
        if len(to_follow)>nb_user:
            to_follow=random.sample(to_follow,nb_user)
            pin_list=[]
            thread_list=[]
            lock=Lock()
            for u in to_follow:
                print u
                def task(url,user_id):
                    pin_page=PinListPage('{0}/pins/?page='.format(url), user_id)
                    pin_page.fetch(1)
                    lock.acquire()
                    pin_list.extend(pin_page.pin_list)
                    lock.release()
                t=Thread(target=task,args=(u.url(),u.id,))
                thread_list.append(t)
                
            for t in thread_list:
                t.start()
            for t in thread_list:
                t.join()
            pin_list.sort(key=lambda pin:-pin.nb_repin)
            pin_list=pin_list[:(nb*3)]

            return random.sample(pin_list, nb*(nb<len(pin_list)))
            
    def saveDB(self): # AVOIR
        try:
            u=UserModel.objects.get(user_id=self.id)
            u.name=self.name
            u.location=self.location
            u.photo_url=self.photo_url
            u.save()
        except UserModel.DoesNotExist:
            u=UserModel.objects.create(user_id=self.id,
                                     name=self.name,
                                     location=self.location,
                                     photo_url=self.photo_url)
        
        d=datetime.datetime.now()
        if self.nb_repin:
            try:
                u.userstatmodel_set.get(date__year=d.year, date__month=d.month, date__day=d.day)
            except UserStatModel.DoesNotExist:
                u.userstatmodel_set.create(date= d,
                                           nb_board=self.nb_board,
                                           nb_pin=self.nb_pin,
                                           nb_like=self.nb_like,
                                           nb_followers=self.nb_followers,
                                           nb_following=self.nb_following,
                                           nb_comment=self.nb_comment,
                                           nb_repin=self.nb_repin,
                                           nb_liked=self.nb_liked
                                           )
        return u
    
    def calcLatLng(self):
        # Get the user or create a new one.
        if self.location !=None:
            try:  
                u_model = UserModel.objects.get(pk=self.id)               
            except UserModel.DoesNotExist:
                u_model = UserModel.objects.create(pk=self.id, address=self.location)
            
            u_model.address = self.location # User address update on the db
            u_model.save()
            
            # Get the (lat,lng) or use geocoding 
            try:
                loc_model=LocationModel.objects.get(pk=u_model.address)
                self.lat,self.lng=(loc_model.lat,loc_model.lng)
            except LocationModel.DoesNotExist:
                try:
                    self.lat, self.lng =addressToLatLng(self.location) # Geocoding
                    LocationModel.objects.create(address=self.location, lat=self.lat, lng=self.lng) # Mise à jour de la base  
                except Exception as e:
                    print e.args
                    
    def getFollowGroups(self,limit=1):
        f_list=[]
        group_list=[]
        for f in self.fetchFollowers(1):
            if f.lat !=None and f.lng != None:
                
                f_list.append([f,True])
            
        for f in self.fetchFollowing(1):
            if f.lat !=None and f.lng != None:
                f_list.append([f,False])
                
        if f_list !=[]:
            f_list.sort(key=lambda x:(x[0].lat,x[0].lng))
            prec_lat=f_list[0][0].lat 
            prec_lng=f_list[0][0].lng
            
            group_list.append([])
            j=0
            group_list[0].append(f_list[0])
             
            for i in range(1,len(f_list)):
                if (prec_lat !=f_list[i][0].lat) or (prec_lng != f_list[i][0].lng):
                    j+=1
                    group_list.append([])         
                group_list[j].append(f_list[i])    
                prec_lat=f_list[i][0].lat 
                prec_lng=f_list[i][0].lng
        return group_list

    def getFollowersJSON(self):
        return dumps(self.followers)
    
    def getFollowingJSON(self):
        return dumps(self.following)
## test ##
if __name__=='__main__':
    User.fetchLatestStat()

