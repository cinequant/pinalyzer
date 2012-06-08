# -*- coding: utf-8 -*-
############################
# Pinalyser
# some primitive functions             #
# author: vl@cinequant.com #
############################



import urllib2
import re
import string
import simplejson as json
from map.models import UserModel, LocationModel
from bs4 import BeautifulSoup

# Calculate from an adress, the corresponding geographic coordinates ( a (lat,lng) couple ), using geocoding service ( google map api).
def addressToLatLng(address):
    adr=string.replace(address, ' ', '+') 
    html_file=urllib2.urlopen('https://maps.googleapis.com/maps/api/geocode/json?address='+adr+'&sensor=false')
    json_output=html_file.read()
    output=json.loads(json_output)
    
    if output['status'] != "OK":
        raise Exception('status ='+output['status'])
    
    return (output['results'][0]['geometry']['location']['lat'],output['results'][0]['geometry']['location']['lng'])

class User:  
    def __init__(self,id,location=None, name=None, photo_url=None):
        self.id=id # User id in pinterest, each user have a unique id
        self.name=name #User displayed name
        self.photo_url=photo_url 
        self.location=location #User location , a string like "Paris,France"
        
        self.lat=None # Latitude
        self.lng=None # Longitude
        self.followers=[] 
        self.following=[]      
            
    def fetchFollowers(self):
        print "followers pour "+str(self.id)
        url="http://pinterest.com/"+str(self.id)+"/followers/"
        htmlfile=urllib2.urlopen(url)
        source=htmlfile.read()
        
        #get the total number of pages in the results (pages are loaded via AJAX) but we can hack that
        page_s=re.findall("totalPages.*",source)[0]
        total_pages=int(page_s[12:-1])
        print total_pages
        

        follower_list=[]
        soup=BeautifulSoup(source)
        follower_list_html=soup.find_all('div',attrs={'class':'person'})          
        for follower in follower_list_html:
            # follower photo url
            f_photo=follower.find('a')['style'][22:-1]
            
            # follower id 
            f_tag=follower.find_all('a')[1]
            f_id=f_tag['href'][1:-1]
            print f_id
            
            #follower namme
            f_name=f_tag.contents[0]
            # follower location
            f_loc=follower.find('span',{'class':'location'})
            if f_loc != None :
                f_loc=f_loc.next_sibling
                f_loc=re.sub("\n", "",f_loc)         
                print "LOCALISE :"+f_loc
        
            u=User(f_id,f_loc,f_name,f_photo)
            try:
                u.calcLatLng()
            except Exception as ex:
                print ex.args
            follower_list.append(u)
    #print follower_list
    
        self.followers=follower_list
        return follower_list

    def fetchFollowing(self):
        print "following pour "+str(self.id)
        url="http://pinterest.com/"+str(self.id)+"/following/"
        htmlfile=urllib2.urlopen(url)
        source=htmlfile.read()
        page_s=re.findall("totalPages.*",source)[0]
        total_pages=int(page_s[12:-1])
        print total_pages
        
        following_list=[]
        soup=BeautifulSoup(source)
        following_list_html=soup.find_all('div',attrs={'class':'person'})
        for following in following_list_html:
            
            #following photo url
            f_photo=following.find('a')['style'][22:-1]
            # following id 
            f_tag=following.find_all('a')[1]
            f_id=f_tag['href'][1:-1]
            print f_id
            
            #following name
            f_name=f_tag.contents[0]
            # following location
            f_loc=following.find('span',{'class':'location'})
            if f_loc != None : 
                f_loc=f_loc.next_sibling
                f_loc=re.sub("\n", "",f_loc)        
                print f_loc
        
            u=User(f_id,f_loc,f_name,f_photo)
            try:
                u.calcLatLng()
            except Exception as ex:
                print ex.args
            following_list.append(u)
            
        self.following=following_list
        return following_list

    def searchUser(self,id):    
        url="http://pinterest.com/search/people/?q="+str(id)
        htmlfile=urllib2.urlopen (url)
        source=htmlfile.read ()
        soup = BeautifulSoup(source)
        user_list= soup.find_all('div',attrs={'class':'pin user'})
        print user_list
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


#######
#test

