# -*- coding: utf-8 -*-
import cStringIO
import Image
import urllib3

class Pin(object):
    http = urllib3.PoolManager()
    
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
    @staticmethod
    def modelToPin(pin_model):
        p=Pin(pin_model.pin_id, pin_model.url, pin_model.pinner_id, pin_model.pinner_name,  pin_model.board_id,  pin_model.board_name,  pin_model.width,  pin_model.height)
        return p
    
    def __init__(self, pin_id, pin_url, pinner_id, pinner_name, board_id, board_name, width=None, height=None,nb_repin=0,nb_comment=0,nb_like=0):
        self.pin_id=pin_id
        self.pin_url=pin_url
        self.pinner_id=pinner_id
        self.pinner_name=pinner_name
        self.board_id=board_id
        self.board_name=board_name
        self.width=width
        self.height=height
        self.nb_repin=nb_repin
        self.nb_comment=nb_comment
        self.nb_like=nb_like
    
    def __str__(self):
        return '{self.pin_id}, {self.pin_url}, {self.pinner_id}, {self.pinner_name}, {self.board_id}, {self.board_name}, {self.width}, {self.height},, {self.nb_repin}, {self.nb_comment}, {self.nb_like}'.format(self=self)
    
    def __hash__(self):
        return hash(self.pin_id)
    
    def __eq__(self,o):
        return self.pin_id==o.pin_id
    
    def get_larger_url(self):
        return self.pin_url[:-5]+'f'+self.pin_url[-4:]
    
    def setDim(self):
        r=Pin.http.request('GET',self.get_larger_url())
        im= cStringIO.StringIO(r.data) # constructs a StringIO holding the image
        img=Image.open(im)
        self.width, self.height=img.size             

if __name__ =='__main__':
    pass
    