# -*- coding: utf-8 -*-
from models import CategoryModel
from django.db import  IntegrityError
import re
import cStringIO
import Image
import urllib3

class Category:
    # Pool manager
    http = urllib3.PoolManager()
    # Reg exp pin
    re_pin_html=re.compile('<div class="pin".*?</body>',re.DOTALL)
    re_pin_id=re.compile('<a href="/pin/(?P<pinId>[0-9]+?)/" class="PinImage ImgLink">')
    re_pin_url=re.compile('<img src="(?P<pinUrl>.*?)"')
    re_pin_more=re.compile('<a href="/(?P<pinnerId>.+?)/">(?P<pinnerName>.+?)</a> onto <a href="/(.+?)/(?P<boardId>.+?)/">(?P<boardName>.+?)</a>')
    # Reg exp category
    re_cat_div=re.compile('<div id="CategoriesBar" >.*?</div>',re.DOTALL)
    re_cat=re.compile('<a href="/all/\?category=(?P<cat_id>.+?)" >(?P<cat_name>.+?)</a>')
    
    @staticmethod
    def searchPinId(pin_div):
        match=re.search(Category.re_pin_id,pin_div)
        return match.group('pinId')
    
    @staticmethod
    def searchPinUrl(pin_div):
        match=re.search(Category.re_pin_url,pin_div)
        return match.group('pinUrl')
    
    @staticmethod
    def searchPinMore(pin_div):
        match=re.search(Category.re_pin_more,pin_div)
        return (match.group('pinnerId'), match.group('pinnerName'), match.group('boardId'), match.group('boardName'),)
    
    @staticmethod
    def fetchCategories():
        r=Category.http.request('GET','http://pinterest.com')
        match=re.search(Category.re_cat_div,r.data)
        for m in re.finditer(Category.re_cat, match.group(0)):
            cat=Category(m.group('cat_id'),m.group('cat_name'))
            print cat
            cat.createDB()     
        cat=Category('popular','Popular')
        cat.createDB()
    
    @staticmethod 
    def fetchNewPins():
        for cat in CategoryModel.objects.all():
            c=Category(cat.category_id,cat.category_name)
            try:
                c.fetchPin(limit=2)
            except Exception:
                print '1 pin a echoué'
    
    def __init__(self, cat_id, cat_name):
        self.cat_id=cat_id
        self.cat_name=cat_name
    
    def __unicode__(self):
        return '{self.cat_id}, {self.cat_name}}'.format(self=self)
    
    
    def fetchPin(self,limit=1):
        for page in range(1,limit+1):
            r=Category.http.request('GET',self.url_cat(page))
            
            splitter=re.compile('<div class="pin"',re.DOTALL)
            pin_div_list=splitter.split(re.search(Category.re_pin_html,r.data).group(0))[1:]
            for pin_div in pin_div_list:
                pin_id=unicode(Category.searchPinId(pin_div))
                pin_url=Category.searchPinUrl(pin_div)
                pinner_id,pinner_name,board_id,board_name=Category.searchPinMore(pin_div)
                
                if pin_url != 'http://passets-ec.pinterest.com/images/VideoIndicator.png':
                    p=Pin(pin_id, pin_url,pinner_id, pinner_name, board_id, board_name)
                    p.setDim(p.get_larger_url())
                    print p
                    self.addPinDB(p)
    
    def url_cat(self,page=1):
        if self.cat_id==None or self.cat_id=='' or self.cat_id=='popular':
            return 'http://pinterest.com/popular/?'
        else:
            return'http://pinterest.com/all/?category='+str(self.cat_id)+'&lazy=1&page='+str(page)
    
    def createDB(self):
        try:
            CategoryModel.objects.create(category_id=self.cat_id, category_name=self.cat_name)
        except IntegrityError:
            print 'Category already present in the database'
            
    def addPinDB(self,pin):
        cat=CategoryModel.objects.get(category_id=self.cat_id)
        try:
            cat.pinmodel_set.create(pin_id=pin.pin_id, url=pin.pin_url, pinner_id=pin.pinner_id, pinner_name=pin.pinner_name, board_id=pin.board_id, board_name=pin.board_name, width=pin.width, height=pin.height)            
        except IntegrityError:
            print 'Pin already in the database'      

class Pin:
    @staticmethod
    def fetchPin(limit=1, cat_id=None):
        cat=Category(cat_id, None)
        cat.fetchPin(limit)
    
    @staticmethod
    def getNewScore(score_pin1, score_pin2, pin1_win):
        f=400.0 # Coef pour étendre la plage de valeur
        k=10
        diff1=max(min(score_pin1-score_pin2, 400),-400)
        diff2=-diff1
        p1=1.0/(1.0+pow(10.0,-float(diff1)/f))
        p2=1.0/(1.0+pow(10.0,-float(diff2)/f))
        new_score_pin1=int(score_pin1 + k*(float(pin1_win)-p1))
        new_score_pin2=int(score_pin2 + k*(float(not pin1_win)-p2))
        return (new_score_pin1,new_score_pin2)
    
    def __init__(self, pin_id, pin_url, pinner_id, pinner_name, board_id, board_name, width=None, height=None):
        self.pin_id=pin_id
        self.pin_url=pin_url
        self.pinner_id=pinner_id
        self.pinner_name=pinner_name
        self.board_id=board_id
        self.board_name=board_name
        self.width=width
        self.height=height
    
    def __str__(self):
        return '{self.pin_id}, {self.pin_url}, {self.pinner_id}, {self.pinner_name}, {self.board_id}, {self.board_name}, {self.width}, {self.height}'.format(self=self)
        
    def get_larger_url(self):
        return self.pin_url[:-5]+'f'+self.pin_url[-4:]
    
    def setDim(self,url):
        r=Category.http.request('GET',url)
        im= cStringIO.StringIO(r.data) # constructs a StringIO holding the image
        img=Image.open(im)
        self.width, self.height=img.size             

if __name__ =='__main__':
    pass
    