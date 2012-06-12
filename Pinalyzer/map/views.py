# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from user import User
import simplejson as json

def index(request):
    try:
        user_id=request.REQUEST['user_id']
    except KeyError:
        return render_to_response('map/index.html')
    
    u=User(user_id)
    
    f_list=[]
    group_list=[]
    for f in u.fetchFollowers(1):
        print f.lat
        if f.lat !=None and f.lng != None:
            
            f_list.append([f,True])
        
    for f in u.fetchFollowing(1):
        if f.lat !=None and f.lng != None:
            f_list.append([f,False])
            
    if f_list !=[]:
        f_list.sort(key=lambda x:(x[0].lat,x[0].lng))
        
        prec_lat=f_list[0][0].lat 
        prec_lng=f_list[0][0].lng
        
        group_list.append([])
        j=0
        group_list[0].append(f_list[0])
         
        for i in range(1,len(f_list)):
            if (prec_lat !=f_list[i][0].lat) or (prec_lng != f_list[i][0].lng):
                j+=1
                group_list.append([])         
            group_list[j].append(f_list[i])    
            prec_lat=f_list[i][0].lat 
            prec_lng=f_list[i][0].lng   
            
    return render_to_response('map/index.html',{'group_list':json.dumps(group_list,default=User.encode_user)})


