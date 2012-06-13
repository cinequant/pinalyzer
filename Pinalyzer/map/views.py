# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from user import User
from map.models import PinModel
import simplejson as json
import random
from django.http import HttpResponse

def index(request):
    try:
        user_id=request.REQUEST['user_id']
    except KeyError:
        return render_to_response('map/index.html')
    
    u=User(user_id)  
    group_list=u.getFollowGroups() # all followers and following grouped by location            
    return render_to_response('map/index.html',{'group_list':json.dumps(group_list,default=User.encode_user)})

def ranking(request):
    pin_list=PinModel.objects.all().order_by('score')
    print len(pin_list)
    return render_to_response('map/images.html',{'pin_list':pin_list})

def vote(request):
    if request.is_ajax():
        pin_list=PinModel.objects.all().order_by('score')
        i=int(random.random()*len(pin_list)/10)
        j=int(random.random()*len(pin_list)/10)
        if i==j:
            if i==0:
                j+=1
            else:
                j-=1
        pin1=PinModel.objects.get(id=i)
        pin2=PinModel.objects.get(id=j)
        response_data=[pin1,pin2]
        return HttpResponse(json.dumps(response_data), mimetype='application/json')
    else:
        return render_to_response('map/vote.html')

    
    
    




