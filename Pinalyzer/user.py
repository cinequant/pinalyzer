# -*- coding: utf-8 -*-
############################
# Pinalyser
# some primitive functions             #
# author: vl@cinequant.com #
############################

import urllib3
import re
import string
import simplejson as json
from map.models import UserModel, LocationModel
from django.utils.encoding import smart_unicode
from bs4 import BeautifulSoup

re_user=re.compile('class="PersonImage ImgLink" style="background-image: url\((?P<photo>.+?)\)">'+'.*?'
+'<h4><a href="/(?P<id>.+?)/">(?P<name>.+?)</a></h4>'+'.*?'
+'((<span class="icon location"></span>(?P<location>.+?(?=\n)))|PersonPins">)', re.DOTALL)
re_marker=re.compile('\.pageless\({(.*)"marker": (?P<marker>.+?)(?=\n)',re.DOTALL)
re_html_pers=re.compile('<div class="person">.*?<div class="PersonPins">',re.DOTALL)

http = urllib3.PoolManager()

# Calculate from an adress, the corresponding geographic coordinates ( a (lat,lng) couple ), using geocoding service ( google map api).
def addressToLatLng(address):
    adr=string.replace(address, ' ', '+') 
    r=http.request('GET','https://maps.googleapis.com/maps/api/geocode/json?address='+adr+'&sensor=false')
    json_output=r.data
    output=json.loads(json_output)
    
    if output['status'] != "OK":
        
        raise Exception('status ='+output['status'])
    
    return (output['results'][0]['geometry']['location']['lat'],output['results'][0]['geometry']['location']['lng'])


             
def searchId(person_html):
    match=re.search('<a href="/(?P<id>.*)/"',person_html)
    return match.group('id')
                
def searchPhoto(person_html):
    match=re.search('class="PersonImage ImgLink" style="background-image: url\((?P<photo>.+?)\)">',person_html)
    return match.group('photo')
             
def searchName(person_html):
    match=re.search('<h4><a href="/.+?/">(?P<name>.+?)</a></h4>',person_html)
    if match == None:
        raise Exception('No name')
    return match.group('name')

def searchLocation(person_html):
    match=re.search('<span class="icon location"></span>(?P<location>.+)',person_html)
    if match == None:
        raise Exception('No location')
    return match.group('location')


def searchPersons(source):
    html_list= re.findall(re_html_pers,source) 
    return html_list

def searchUserInfo(person_html):
    match=re.search(re_user,person_html)
    f_id=match.group('id')
    f_loc=match.group('location')
    f_name=match.group('name')      
    f_photo=match.group('photo')
    return (f_id,f_loc,f_name,f_photo)  

def searchMarker(person_html):
    match=re.search(re_marker,person_html)
    return int(match.group('marker'))         

class User:
    def __init__(self,user_id,location=None, name=None, photo_url=None):
        self.id=user_id # User id in pinterest, each user have a unique id
        self.name=name # User displayed name
        self.photo_url=photo_url 
        self.location=location #User location , a string like "Paris,France"
        self.lat=None # Latitude
        self.lng=None # Longitude
        self.followers=[] 
        self.following=[]
        
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
                print f_loc
                u=User(f_id,f_loc,f_name,f_photo)
                try:
                    u.calcLatLng()
                except Exception as e:
                    print e.args
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
    
    def searchUser(self,user_id):    
        url="http://pinterest.com/search/people/?q="+str(user_id)
        r=http.request ('GET',url)
        source=r.data
        soup = BeautifulSoup(r.data)
        user_list= soup.find_all('div',attrs={'class':'pin user'})
        return user_list
    
    def calcLatLng(self):
        # Get the user or create a new one.
        if self.location !=None:
            try:  
                u_model = UserModel.objects.get(pk=self.id)
                print "existe bien"                 
            except UserModel.DoesNotExist:
                print "existe pas encore"
                u_model = UserModel.objects.create(pk=self.id, address=self.location)
            
            u_model.address = self.location # User address update on the db
            u_model.save()
            
            # Get the (lat,lng) or use geocoding 
            try:
                loc_model=LocationModel.objects.get(pk=u_model.address)
                print "est bien localisé"
                self.lat,self.lng=(loc_model.lat,loc_model.lng)
            except LocationModel.DoesNotExist:
                print "pas encore localisé"
                self.lat, self.lng =addressToLatLng(self.location) # Geocoding
                LocationModel.objects.create(address=self.location, lat=self.lat, lng=self.lng) # Mise à jour de la base  
            
        
    def getFollowersJSON(self):
        return json.dumps(self.followers)
    
    def getFollowingJSON(self):
        return json.dumps(self.following)  
    
    @staticmethod
    def encode_user(obj):
        if not isinstance(obj, User):
            raise TypeError("%r is not JSON serializable" % (obj))
        return obj.__dict__
    
## test ##



