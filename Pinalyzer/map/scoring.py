# -*- coding: utf-8 -*-
import urllib3
import re
import random

class Scoring:
    # User scoring informations
    http = urllib3.PoolManager()
    re_contextbar=re.compile('<div id="ContextBar".*?'
                             +'.*?<strong>(?P<nb_pin>[0-9]+)</strong> Pins.*?'
                             +'<li>.*?<strong>(?P<nb_followers>[0-9]+)</strong> Followers.*?</li>.*?'
                             +'',re.DOTALL)
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
        self.nb_pin=None
        self.nb_followers=None
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
        match=re.search(Scoring.re_contextbar,r.data)
        self.nb_pin=int(match.group('nb_pin'))
        self.nb_followers=int(match.group('nb_followers'))
        
    def fetchPinsInfo(self, nb_pages=1):
        self.nb_like=0
        self.nb_comment=0
        self.nb_repin=0
        
        if self.nb_pin == None:
            self.fetchInfo()
        
        total_pages=min(self.nb_pin/50 + (self.nb_pin%50 !=0),10)
        list_page= random.sample(range(1,total_pages+1),nb_pages)
        self.sampled_pin=0
        for page in list_page:
            r=Scoring.http.request('GET', self.pins_url(page))
            pin_div_list=Scoring.splitter.split(re.search(Scoring.re_pin_html,r.data).group(0))[1:]
            for pin_div in pin_div_list:
                print pin_div
                self.sampled_pin+=1
                self.nb_like+=Scoring.searchLike(pin_div)
                self.nb_comment+=Scoring.searchComment(pin_div)
                self.nb_repin+=Scoring.searchRepin(pin_div)
                print (self.nb_like, self.nb_comment, self.nb_repin, self.sampled_pin)
                
    def fetch(self):
        self.fetchInfo()
        self.fetchPinsInfo(1)
    
    def getScore(self): # A voir
        return self.nb_followers+self.nb_repin+self.nb_comment+self.nb_like
    
    def getMoyLike(self):
        return float(self.nb_like)/float(self.sampled_pin)
    
    def getMoyComment(self):
        return float(self.nb_comment)/float(self.sampled_pin)
    
    def getMoyRepin(self):
        return float(self.nb_repin)/float(self.sampled_pin)
    
    
if __name__=='__main__':
    s=Scoring('sudzilla')
    s.fetchPinsInfo()