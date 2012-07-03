# -*- coding: utf-8 -*-
import urllib3
import re
import random

      
class NotFound(Exception):
    pass

class Scoring:
    # User scoring informations
    http = urllib3.PoolManager()
    re_title=re.compile('<title>(?P<title>.*?)</title>')
    re_contextbar=re.compile('<div id="ContextBar".*?'
                             +'.*?<strong>(?P<nb_board>[0-9]+)</strong> Boards?.*?'
                             +'.*?<strong>(?P<nb_pin>[0-9]+)</strong> Pins?.*?'
                             +'.*?<strong>(?P<nb_liked>[0-9]+)</strong> Likes?.*?'
                             +'<li>.*?<strong>(?P<nb_followers>[0-9]+)</strong> Followers.*?</li>.*?'
                             +'<li>.*?<strong>(?P<nb_following>[0-9]+)</strong> Following.*?</li>.*?',re.DOTALL)
    re_pin_html=re.compile('<div class="pin".*?</body>',re.DOTALL)
    re_repin=re.compile('<span class="RepinsCount">(.*?)(?P<nb_repins>[0-9]+) repin(s)?(.*?)</span>',re.DOTALL)
    re_like=re.compile('<span class="LikesCount">(.*?)(?P<nb_likes>[0-9]+) like(s)?(.*?)</span>',re.DOTALL)
    re_comment=re.compile('<span class="CommentsCount">(.*?)(?P<nb_comments>[0-9]+) comment(s)?(.*?)</span>',re.DOTALL)
    splitter=re.compile('<div class="pin"',re.DOTALL)
    
    @staticmethod
    def searchLike(pin_div):
        match=re.search(Scoring.re_like,pin_div)
        
        if match != None:
            return int(match.group('nb_likes'))
        else:
            return 0
    
    @staticmethod
    def searchComment(pin_div):
        match=re.search(Scoring.re_comment,pin_div)
        if match != None:
            return int(match.group('nb_comments'))
        else:
            return 0
    
    @staticmethod
    def searchRepin(pin_div):
        match=re.search(Scoring.re_repin,pin_div)
        if match != None:    
            return int(match.group('nb_repins'))
        else:
            return 0
        
    def __init__(self,user_id):
        self.id=user_id
        self.nb_board=None
        self.nb_pin=None
        self.nb_liked=None
        self.nb_followers=None
        self.nb_following=None
        self.nb_like=0
        self.nb_repin=0
        self.nb_comment=0
        self.sampled_pin=0
    
    def pins_url(self,page):
        return 'http://pinterest.com/'+str(self.id)+'/pins?lazy=1&page='+str(page)
    
    def main_url(self):
        return 'http://pinterest.com/'+str(self.id)
    
    def fetchInfo(self):
        r=Scoring.http.request('GET',self.main_url())
        print r.data
        match=re.search(Scoring.re_title,r.data)
        if match != None and match.group('title') =='Pinterest - 404':
            print 'title none'
            raise NotFound
        
        match=re.search(Scoring.re_contextbar,r.data)
        
        self.nb_board=int(match.group('nb_board'))
        self.nb_pin=int(match.group('nb_pin'))
        self.nb_liked=int(match.group('nb_liked'))
        self.nb_followers=int(match.group('nb_followers'))
        self.nb_following=int(match.group('nb_following'))
        
    def fetchPinsInfo(self, nb_pages=10):
        self.nb_like=0
        self.nb_comment=0
        self.nb_repin=0
        
        
        if self.nb_pin == None:
            self.fetchInfo()
        
        total_pages=min(self.nb_pin/50 + (self.nb_pin%50 !=0),10)
        nb_pages=min(10, total_pages)
        list_page= random.sample(range(1,total_pages+1),nb_pages)
        
        self.sampled_pin=0
        for page in list_page:
            r=Scoring.http.request('GET', self.pins_url(page))
            pin_div_list=Scoring.splitter.split(re.search(Scoring.re_pin_html,r.data).group(0))[1:]
            for pin_div in pin_div_list:
                self.sampled_pin+=1
                self.nb_like+=Scoring.searchLike(pin_div)
                self.nb_comment+=Scoring.searchComment(pin_div)
                self.nb_repin+=Scoring.searchRepin(pin_div)
                print (self.nb_like, self.nb_comment, self.nb_repin, self.sampled_pin)
        
             
        if self.nb_pin !=self.sampled_pin:
            self.nb_like=int(float(self.nb_like)*float(self.nb_pin)/float(self.sampled_pin))
            self.nb_comment=int(float(self.nb_comment)*float(self.nb_pin)/float(self.sampled_pin))
            self.nb_repin=int(float(self.nb_repin)*float(self.nb_pin)/float(self.sampled_pin))
                
    def fetch(self):
        self.fetchInfo()
        self.fetchPinsInfo()
    
    
if __name__=='__main__':
    s=Scoring('sudzilla')
    s.fetchInfo()
    s.fetchPinsInfo()
    
    print (s.id,s.nb_board,s.nb_pin, s.nb_liked, s.nb_followers, s.nb_following)