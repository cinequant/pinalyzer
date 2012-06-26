# -*- coding: utf-8 -*-
############################
# Pinalyser
# some primitive functions             #
# author: vl@cinequant.com #
############################
from django.db import  IntegrityError
from django.utils.simplejson import loads, dumps
from models import UserModel, LocationModel
from scoring import  Scoring


import urllib3
import re
import string

# the person div reg exp('/user_id/followers/' or '/user_id/following/')
re_html_pers=re.compile('<div class="person">.*?<div class="PersonPins">',re.DOTALL)
# Person informations (id,name,photo,location)
re_user=re.compile('class="PersonImage ImgLink" style="background-image: url\((?P<photo>.+?)\)">'+'.*?'
                   +'<h4><a href="/(?P<id>.+?)/">(?P<name>.+?)</a></h4>'+'.*?'
                   +'((<span class="icon location"></span>(?P<location>.+?(?=\n)))|PersonPins">)', re.DOTALL) 
# Marker value ('pinterest.com/user_id/followers/' or 'pinterest.com/user_id/following/')
re_follow_marker=re.compile('\.pageless\({(.*?)"marker": (?P<marker>.+?)(?=\n)',re.DOTALL)
http = urllib3.PoolManager()

def searchPersons(source):
    html_list= re.findall(re_html_pers,source) 
    return html_list

def searchUserInfo(person_html):
    match=re.search(re_user,person_html)
    f_id=match.group('id')
    f_loc=match.group('location')
    if f_loc != None:
        f_loc=f_loc.decode('utf-8')  
    f_name=match.group('name')      
    f_photo=match.group('photo')
    return (f_id,f_loc,f_name,f_photo)  

def searchMarker(person_html):
    match=re.search(re_follow_marker,person_html)
    return int(match.group('marker'))



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
        
    def __init__(self,user_id,location=None, name=None, photo_url=None):
        self.id=user_id # User id in pinterest, each user have a unique id
        self.name=name # User displayed name
        self.photo_url=photo_url 
        self.scoring=None
        self.followers=[]
        self.following=[]
        
        self.location=location #User location , a string like "Paris,France"
        self.lat=None # Latitude
        self.lng=None # Longitude
        
    def fetchScoring(self):
        self.scoring=Scoring(self.id)
        self.scoring.fetch()
        
    def getScore(self):
        return self.scoring.getScore()
    
    def getNbFollowers(self):
        return self.scoring.nb_followers
    
    def getNbPin(self):
        return self.scoring.nb_pin
    
    def saveDB(self):
        u,created=UserModel.objects.get_or_create(user_id=self.id)
        u.score=self.getScore()
        u.nb_followers=self.getNbFollowers()
        u.nb_pins=self.getNbPin()
        u.save()
        return u
        
    def fetchFollow(self,follow, limit):
        follow_list=[]

        url='http://pinterest.com/'+str(self.id)+'/'+follow # follow variable could be 'following or 'followers'
        marker=0 # Used to http GET each pages
        page=1 # Used to http GET each pages
        
        while marker >=0 and page<=limit:
            r = http.request('GET', url+'/?page='+str(page)+'&marker='+str(marker))
            source=r.data
            html_list=searchPersons(source)  
                       
            for person_html in html_list:
                f_id,f_loc,f_name,f_photo=searchUserInfo(person_html)
                print (f_id,f_loc)
                u=User(f_id,f_loc,f_name,f_photo)
                u.calcLatLng()
                follow_list.append(u)
                
                                   
            marker=searchMarker(source) # Next marker (must be parsed on the html page)
            page+=1 # Next page
                        
        return follow_list

    def fetchFollowers(self,limit=5):
        self.followers=self.fetchFollow('followers',limit)
        return self.followers

    def fetchFollowing(self,limit=5):
        self.following=self.fetchFollow('following',limit)
        return self.following
    
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
    u= User('sudzilla')
    u.fetchScoring()
    u.saveDB()

