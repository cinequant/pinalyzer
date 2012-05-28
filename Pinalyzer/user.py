# -*- coding: utf-8 -*-

############################
# Pinalyser
# some primitive functions             #
# author: vl@cinequant.com #
############################

import re
from BeautifulSoup import BeautifulSoup
import MySQLdb
import codecs
import os
import urllib2
import urllib
import simplejson as json


class user:

    followers=[]
    following=[]
    
    def __init__(self,id,location=None):
        self.id=id
        self.location=location
            
    def fetchFollowers(self):
        print "followers pour "+str(self.id)
        url="http://pinterest.com/"+str(self.id)+"/followers/"
        file=urllib2.urlopen(url)
        source=file.read(2000000)
        #get the total number of pages in the results (pages are loaded via AJAX) but we can hack that
        page_s=re.findall("totalPages.*",source)[0]
        total_pages=int(page_s[12:-1])
        print total_pages

        follower_list=[]
        soup=BeautifulSoup(source)
        follower_list_html=soup.findAll('div',attrs={'class':'person'})
        for follower in follower_list_html:
            a=follower.findAll('a')[2]['href']
            print a
            follower_list.append(a)
    #print follower_list
    
        self.followers=follower_list
        return follower_list

    def fetchFollowing(self):
        print "following pour "+str(self.id)
        url="http://pinterest.com/"+str(self.id)+"/following/"
        file=urllib2.urlopen(url)
        source=file.read(2000000)
        page_s=re.findall("totalPages.*",source)[0]
        total_pages=int(page_s[12:-1])
        print total_pages
        following_list=[]
        soup=BeautifulSoup(source)
        following_list_html=soup.findAll('div',attrs={'class':'person'})
        for following in following_list_html:
            a=following.findAll('a')[2]['href']
            print a
            following_list.append(a)
    #print follower_list
        self.following=following_list
        return following_list

    
    def getFollowersJSON(self):
        return json.dumps(self.followers)
    
    def getFollowingJSON(self):
        return json.dumps(self.following)
    

def searchUser(id):    
    url="http://pinterest.com/search/people/?q="+str(id)
    file=urllib2.urlopen (url)
    source=file.read (2000000)
    soup = BeautifulSoup(source)
    user_list= soup.findAll('div',attrs={'class':'pin user'})
    print user_list
    return user_list

def fetchFollowers(id):
    url="http://pinterest.com/"+str(id)+"/followers/"
    file=urllib2.urlopen(url)
    source=file.read(2000000)
    soup=BeautifulSoup(source)
    follower_list=soup.findAll('div',attrs={'class':'person'})
    for follower in follower_list:
        a=follower.findAll('a')[2]['href']
        print a
    #print follower_list
    return follower_list

#######
#test

u=user('mmanion')
u.fetchFollowers()
u.fetchFollowing()
print u.getFollowersJSON()