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


class user:

    
    
    def __init__(self,id,location=None):
        self.id=id
        self.location=location
        self.followers=[]
        self.following=[]      
            
    def fetchFollowers(self):
        print "followers pour "+str(self.id)
        url="http://pinterest.com/"+str(self.id)+"/followers/"
        htmlfile=urllib2.urlopen(url)
        source=htmlfile.read(2000000)
        #get the total number of pages in the results (pages are loaded via AJAX) but we can hack that
        page_s=re.findall("totalPages.*",source)[0]
        total_pages=int(page_s[12:-1])
        print total_pages

        follower_list=[]
        soup=BeautifulSoup(source)
        follower_list_html=soup.findAll('div',attrs={'class':'person'})
        
        for follower in follower_list_html:
            # follower id 
            f_id=follower.findAll('a')[2]['href']
            print f_id
            # follower location
            f_loc=follower.find('span',{'class':'location'})
            if f_loc != None : 
                f_loc=f_loc.next_sibling         
                print f_loc
        
            u=user(f_id,f_loc)
            follower_list.append(u)
    #print follower_list
    
        self.followers=follower_list
        return follower_list

    def fetchFollowing(self):
        print "following pour "+str(self.id)
        url="http://pinterest.com/"+str(self.id)+"/following/"
        htmlfile=urllib2.urlopen(url)
        source=htmlfile.read(2000000)
        page_s=re.findall("totalPages.*",source)[0]
        total_pages=int(page_s[12:-1])
        print total_pages
        
        following_list=[]
        soup=BeautifulSoup(source)
        following_list_html=soup.findAll('div',attrs={'class':'person'})
        
        for following in following_list_html:
            # following id 
            f_id=following.findAll('a')[2]['href']
            print f_id
            # following location
            f_loc=following.find('span',{'class':'location'})
            if f_loc != None : 
                f_loc=f_loc.next_sibling         
                print f_loc
        
            u=user(f_id,f_loc)
            following_list.append(u)
            
    #print follower_list
        self.following=following_list
        return following_list

    
    def getFollowersJSON(self):
    #hjkhkjkhkj
        return json.dumps(self.followers)
    
    def getFollowingJSON(self):
        return json.dumps(self.following)
    

def searchUser(id):    
    url="http://pinterest.com/search/people/?q="+str(id)
    htmlfile=urllib2.urlopen (url)
    source=htmlfile.read (2000000)
    soup = BeautifulSoup(source)
    user_list= soup.findAll('div',attrs={'class':'pin user'})
    print user_list
    return user_list

def fetchFollowers(id):
    url="http://pinterest.com/"+str(id)+"/followers/"
    htmlfile=urllib2.urlopen(url)
    source=htmlfile.read(2000000)
    soup=BeautifulSoup(source)
    follower_list=soup.findAll('div',attrs={'class':'person'})
    
    for follower in follower_list: 
        # follower id 
        f_id=follower.findAll('a')[2]['href']
        print f_id
        # follower location
        f_loc=follower.find('span',{'class':'location'})
        if f_loc != None : 
            f_loc=f_loc.next_sibling         
            print f_loc
        
        u=user(f_id,f_loc)
        follower_list.append(u)
            
    #print follower_list
    return follower_list

#######
#test

u=user('ozdensevren')
for x in u.fetchFollowers():
    print x
print u.fetchFollowing()