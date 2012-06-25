import urllib3
import re
import random

# User scoring informations
re_contextbar=re.compile('<div id="ContextBar".*?'
                         +'.*?<strong>(?P<nb_pins>[0-9]+)</strong> Pins.*?'
                         +'<li>.*?<strong>(?P<nb_followers>[0-9]+)</strong> Followers.*?</li>.*?'
                         +'',re.DOTALL)

re_pin_div=re.compile('<div class="pin".*?(?=<div class="pin")',re.DOTALL)
re_repin=re.compile('<span class="RepinsCount">(.*?)(?P<nb_repins>[0-9]+) repin(s)?(.*?)</span>',re.DOTALL)
re_like=re.compile('<span class="LikesCount">(.*?)(?P<nb_likes>[0-9]+) like(s)?(.*?)</span>',re.DOTALL)
re_comment=re.compile('<span class="CommentsCount">(.*?)(?P<nb_comments>[0-9]+) comment(s)?(.*?)</span>',re.DOTALL)

http = urllib3.PoolManager()

class Scoring:
    def __init__(self,id):
        self.id=id
        self.nb_pin=None
        self.nb_follower=None
        self.nb_like=0
        self.nb_repin=0
        self.nb_comment=0
        self.sampled_pin=0
    
    def pins_url(self,page):
        return 'http://pinterest.com/'+str(self.id)+'/pins?lazy=1&page='+str(page)
    
    def main_url(self):
        return 'http://pinterest.com/'+str(self.id)

    @staticmethod
    def searchLike(pin_div):
        match=re.search(re_like,pin_div)
        
        if match != None:
            return int(match.group('nb_likes'))
        else:
            return 0
    
    @staticmethod
    def searchComment(pin_div):
        match=re.search(re_comment,pin_div)
        if match != None:
            return int(match.group('nb_comments'))
        else:
            return 0
    
    @staticmethod
    def searchRepin(pin_div):
        match=re.search(re_repin,pin_div)
        if match != None:    
            return int(match.group('nb_repins'))
        else:
            return 0
    
    def fetchInfo(self):
        r=http.request('GET',self.main_url())
        match=re.search(re_contextbar,r.data)
        self.nb_pins=match.group('nb_pins')
        self.nb_followers=match.group('nb_followers')
        print self.nb_pins, self.nb_followers
        
    def fetchPinsInfo(self, nb_pages=1):
        self.nb_like=0
        self.nb_comment=0
        self.nb_repin=0
        
        if self.nb_pin == None:
            self.fetchInfo()
        
        total_pages=self.nb_pin/50 + (self.nb_pin%50 !=0)
        list_page= random.sample(range(1,total_pages+1))
        self.sampled_pin=0
        for page in list_page:
            r=http.request('GET', self.pins_url(page))
            for pin_div in re.findall(re_pin_div,r.data):
                self.sampled_pin+=1
                self.nb_like+=Scoring.searchLike(pin_div)
                self.nb_comment+=Scoring.searchComment(pin_div)
                self.nb_repin+=Scoring.searchRepin(pin_div)
                print (self.nb_like, self.nb_comment,self.nb_repin)
    
    def getScore(self): # A voir
        return self.nb_followers+self.nb_repin+self.nb_comment+self.nb_like
    
    
if __name__=='__main__':
    s=Scoring('sudzilla')
    s.fetchPinsInfo()