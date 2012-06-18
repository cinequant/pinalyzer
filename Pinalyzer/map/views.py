# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.simplejson import dumps
from map.models import PinModel, CategoryModel

from user import User, getDim
from django_json import DjangoJSONEncoder

import random


def index(request):
    try:
        user_id=request.REQUEST['user_id']
    except KeyError:
        return render_to_response('map/index.html')
    
    u=User(user_id)  
    group_list=u.getFollowGroups() # all followers and following grouped by location            
    return render_to_response('map/index.html',{'group_list':dumps(group_list,cls=DjangoJSONEncoder)})

def ranking(request):
    pin_list=PinModel.objects.all().order_by('-score')
    print len(pin_list)
    return render_to_response('map/images.html',{'pin_list':pin_list})

@ensure_csrf_cookie
def vote(request):
    if request.is_ajax() and request.method== 'GET':
        try:
            cat=request.GET['category']
            try:
                if cat=='all':
                    pin_list=PinModel.objects.all()
                else:
                    cat_model=CategoryModel.objects.get(category_id=cat)
                    pin_list=cat_model.pinmodel_set.all()
            except CategoryModel.DoesNotExist:
                d={'status': 'ERR','data':'Error: This category does not exist on the database '}
                data = dumps(d,cls=DjangoJSONEncoder)
                return HttpResponse(data, mimetype='application/json')
                  
        except KeyError:
            pin_list=PinModel.objects.all()
            
        if len(pin_list)>1:
            pin_list.order_by('-match')
            i=int(random.random()*len(pin_list)/5)
            j=int(random.random()*len(pin_list)/5)
            if i==j:
                if i==0:
                    j+=1
                else:
                    j-=1
            
            w1,h1=getDim(pin_list[i].url)
            w2,h2=getDim(pin_list[j].url)
            pin1={'pin':pin_list[i],'width':w1,'height':h1}
            pin2={'pin':pin_list[j],'width':w2,'height':h2}

            data = dumps({'status': 'OK','data':[pin1,pin2]},cls=DjangoJSONEncoder)
            return HttpResponse(data, mimetype='application/json')
        
        else:
            d={'status': 'ERR','data':'No pins in this category'}
            data = dumps(d,cls=DjangoJSONEncoder)
            return HttpResponse(data, mimetype='application/json')
    else:
        cat_list=CategoryModel.objects.all()
        return render_to_response('map/vote.html',{'cat_list':cat_list})
    

def savematch(request):
    if request.is_ajax() and request.method =='POST':
        try:
            pin1_id=request.POST['pin1_id']
            pin2_id=request.POST['pin2_id']
            choice=request.POST['choice']
            
            pin1=PinModel.objects.get(pin_id=pin1_id)
            pin2=PinModel.objects.get(pin_id=pin2_id)
            
            diff=pin1.score-pin2.score
            
            pin1.updateScore(pin1.pin_id==choice, diff)
            pin2.updateScore(pin2.pin_id==choice,-diff)
            
            
            msg="OK"
            return HttpResponse(msg)
        
        except KeyError, PinModel.DoesNotExist:
            msg="Votre vote n'a pas été pris en compte :("
            return HttpResponse(msg)
    else:
        msg="Votre vote n'a pas été pris en compte :("
        return HttpResponse(msg)
