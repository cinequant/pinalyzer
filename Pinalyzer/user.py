# -*- coding: utf-8 -*-
############################
# Pinalyser
# some primitive functions             #
# author: vl@cinequant.com #
############################

import re
from bs4 import BeautifulSoup
#import MySQLdb
import codecs
import os
import urllib2
import urllib
import simplejson as json


class User:

    
    
    def __init__(self,id,location=None, name=None, photo_url=None):
        self.id=id
        self.name=name
        self.photo_url=photo_url
        
        self.location=location
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
            print f_photo
            
            # follower id 
            f_tag=follower.find_all('a')[1]
            f_id=f_tag['href'][1:-1]
            print f_id
            
            #follower namme
            f_name=f_tag.contents[0]
            print f_name
            # follower location
            f_loc=follower.find('span',{'class':'location'})
            if f_loc != None :
                f_loc=f_loc.next_sibling
                f_loc=re.sub("\n", "",f_loc)         
                print f_loc
        
            u=User(f_id,f_loc,f_name,f_photo)
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
            print f_photo
            # following id 
            f_tag=following.find_all('a')[1]
            f_id=f_tag['href'][1:-1]
            print f_id
            
            #following name
            f_name=f_tag.contents[0]
            print f_name
            # following location
            f_loc=following.find('span',{'class':'location'})
            if f_loc != None : 
                f_loc=f_loc.next_sibling
                f_loc=re.sub("\n", "",f_loc)        
                print f_loc
        
            u=User(f_id,f_loc,f_name,f_photo)
            following_list.append(u)
            
    #print follower_list
        self.following=following_list
        return following_list

    
    def getFollowersJSON(self):
        return json.dumps(self.followers)
    
    def getFollowingJSON(self):
        return json.dumps(self.following)  

    def searchUser(self,id):    
        url="http://pinterest.com/search/people/?q="+str(id)
        htmlfile=urllib2.urlopen (url)
        source=htmlfile.read ()
        soup = BeautifulSoup(source)
        user_list= soup.find_all('div',attrs={'class':'pin user'})
        print user_list
        return user_list

    @staticmethod
    def encode_user(obj):
        if not isinstance(obj, User):
            raise TypeError("%r is not JSON serializable" % (obj))
        return obj.__dict__


#######
#test


