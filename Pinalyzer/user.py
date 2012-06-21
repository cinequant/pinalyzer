# -*- coding: utf-8 -*-
############################
# Pinalyser
# some primitive functions             #
# author: vl@cinequant.com #
############################


from django.db import  IntegrityError
from django.utils.simplejson import loads, dumps
from map.models import UserModel, LocationModel,CategoryModel

import cStringIO
import Image
import urllib3
import re
import string
from bs4 import BeautifulSoup

# the person div reg exp('/user_id/followers/' or '/user_id/following/')
re_html_pers=re.compile('<div class="person">.*?<div class="PersonPins">',re.DOTALL)

# Person informations (id,name,photo,location)
re_user=re.compile('class="PersonImage ImgLink" style="background-image: url\((?P<photo>.+?)\)">'+'.*?'
                   +'<h4><a href="/(?P<id>.+?)/">(?P<name>.+?)</a></h4>'+'.*?'
                   +'((<span class="icon location"></span>(?P<location>.+?(?=\n)))|PersonPins">)', re.DOTALL) 

# Marker value ('pinterest.com/user_id/followers/' or 'pinterest.com/user_id/following/')
re_follow_marker=re.compile('\.pageless\({(.*?)"marker": (?P<marker>.+?)(?=\n)',re.DOTALL)

# The pin div reg exp
re_pin_div=re.compile('<div class="pin".*?(?=<div class="pin")',re.DOTALL)

# Pin informations ('popular' or '/all/search?category=...'
re_pin_pinId=re.compile('<a href="/pin/(?P<pinId>[0-9]+?)/" class="PinImage ImgLink">')
re_pin_pinUrl=re.compile('<img src="(?P<pinUrl>.*?)"')
re_pin_more=re.compile('<a href="/(?P<pinnerId>.+?)/">(?P<pinnerName>.+?)</a> onto <a href="/(.+?)/(?P<boardId>.+?)/">(?P<boardName>.+?)</a>')

re_cat_div=re.compile('<div id="CategoriesBar" >.*?</div>',re.DOTALL)
re_cat=re.compile('<a href="/all/\?category=(?P<cat_id>.+?)" >(?P<cat_name>.+?)</a>')


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

def searchPinId(pin_div):
    match=re.search(re_pin_pinId,pin_div)
    return match.group('pinId')

def searchPinUrl(pin_div):
    match=re.search(re_pin_pinUrl,pin_div)
    return match.group('pinUrl')

def searchPinMore(pin_div):
    match=re.search(re_pin_more,pin_div)
    return (match.group('pinnerId'), match.group('pinnerName'), match.group('boardId'), match.group('boardName'),)
    
def fetchCategories():
    r=http.request('GET','http://pinterest.com')
    match=re.search(re_cat_div,r.data)
    print match.group(0)
    for m in re.finditer(re_cat,match.group(0)):
        cat_id=m.group('cat_id')
        cat_name=m.group('cat_name')
        try:
            CategoryModel.objects.create(category_id=cat_id,category_name=cat_name)
        except IntegrityError:
            print 'Category already present in the database'
    try:
        CategoryModel.objects.create(category_id='',category_name='')
    except IntegrityError:
        print 'Category already present in the database'
    
        
    

def fetchPin(limit=1,category=None):
    
    if category==None:
        url='http://pinterest.com/popular/?'
        cat=CategoryModel.objects.get(category_id='')
    else:
        url='http://pinterest.com/all/?category='+str(category)+'&'
        cat=CategoryModel.objects.get(category_id=category)
    
    for page in range(1,limit+1):
        r=http.request('GET',url+'lazy=1&page='+str(page))

        for pin_div in re.findall(re_pin_div,r.data):
            pinId=unicode(searchPinId(pin_div))
            pinUrl=searchPinUrl(pin_div)
            pinnerId,pinnerName,boardId,boardName=searchPinMore(pin_div)
            
            print (pinId, pinUrl, pinnerId, pinnerName, boardId, boardName)
            if pinUrl != 'http://passets-ec.pinterest.com/images/VideoIndicator.png':
                
                try:
                    cat.pinmodel_set.create(pin_id=pinId,url=pinUrl,pinner_id=pinnerId,pinner_name=pinnerName,board_id=boardId,board_name=boardName)
                        
                except IntegrityError:
                    print 'Pin already in the database'

# Calculate from an adress, the corresponding geographic coordinates ( a (lat,lng) couple ), using geocoding service ( google map api).
def addressToLatLng(address):
    adr=string.replace(address, ' ', '+') 
    r=http.request('GET','https://maps.googleapis.com/maps/api/geocode/json?address='+adr+'&sensor=false')
    json_output=r.data
    output=loads(json_output)
    
    if output['status'] != "OK":
        raise Exception('status ='+output['status'])
    
    return (output['results'][0]['geometry']['location']['lat'],output['results'][0]['geometry']['location']['lng'])


def getDim(url):
    r=http.request('GET',url)
    im= cStringIO.StringIO(r.data) # constructs a StringIO holding the image
    img=Image.open(im)
    return img.size

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
    
    def searchUser(self,user_id):    
        url="http://pinterest.com/search/people/?q="+str(user_id)
        r=http.request ('GET',url)
        soup = BeautifulSoup(r.data)
        user_list= soup.find_all('div',attrs={'class':'pin user'})
        return user_list
    
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

