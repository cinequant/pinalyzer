# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.utils.simplejson import dumps
from models import PinModel, CategoryModel, UserModel

import random

from user import User
from pin import Pin, Category
from django_json import DjangoJSONEncoder

def index(request):
	try:
		user_id=request.REQUEST['user_id']
	except KeyError:
		return render_to_response('map/index.html')
	
	u=User(user_id)  
	group_list=u.getFollowGroups() # all followers and following grouped by location			
	return render_to_response('map/index.html',{'group_list':dumps(group_list,cls=DjangoJSONEncoder)})

def ranking(request):
	if request.is_ajax() and request.method =='GET':
		
		try:
			cat=request.GET['category']
			try:
				if cat=='all':
					ranking_q=PinModel.objects.all()
				else:
					cat_model=CategoryModel.objects.get(category_id=cat)
					ranking_q=cat_model.pinmodel_set.all()
			except CategoryModel.DoesNotExist:
				d={'status': 'ERR','data':'Error: This category does not exist on the database '}
				data = dumps(d,cls=DjangoJSONEncoder)
				return HttpResponse(data, mimetype='application/json')
		except KeyError:
			ranking_q=PinModel.objects.all()
		
		print type(request.GET['perso'])
		if request.GET['perso']== u'true':
			match_list=request.session['match_list']
			score={}
			
			for t in match_list:
				pin1,pin2,choice=t
				score.setdefault(pin1,0)
				score.setdefault(pin2,0)
				score[pin1], score[pin2]=Pin.getNewScore(score[pin1],score[pin2], choice==pin1)
			
			ranking_list=list(ranking_q.filter(pin_id__in=score.keys()))
			ranking_list.sort(key=lambda pin_model: -score[pin_model.pin_id])
			data=dumps({'status':'OK','data':ranking_list},cls=DjangoJSONEncoder)
			return HttpResponse(data, mimetype='application/json')
		
		if len(ranking_q)>0:
			ranking_q=ranking_q.order_by('-score')[:10]
			ranking_list=[]
			for pin in ranking_q:
				ranking_list.append(pin)
			
			data=dumps({'status':'OK','data':ranking_list},cls=DjangoJSONEncoder)
			return HttpResponse(data, mimetype='application/json')
		else:
			d={'status': 'ERR','data':'Error: No pins in this category'}
			data = dumps(d,cls=DjangoJSONEncoder)
			return HttpResponse(data, mimetype='application/json')
	return render_to_response('map/images.html')

def vote(request):
	if request.is_ajax() and request.method== 'GET':
		
		# Select all pins in a given category
		try:
			cat=request.GET['category']
			try:
				if cat=='all':
					pin_q=PinModel.objects.all()
				else:
					cat_model=CategoryModel.objects.get(category_id=cat)
					pin_q=cat_model.pinmodel_set.all()
			except CategoryModel.DoesNotExist:
				d={'status': 'ERR','data':'Error: This category does not exist on the database '}
				data = dumps(d,cls=DjangoJSONEncoder)
				return HttpResponse(data, mimetype='application/json')
					
		except KeyError:
			pin_q=PinModel.objects.all()
			
		if 'viewed_list' not in request.session :
			request.session['viewed_list']=[]
			
		if 'match_list' not in request.session:
			request.session['match_list']=[]
			
		if len(pin_q)>1:
			# exclude the pins already seen	
			pin_list=pin_q.exclude(pin_id__in=request.session['viewed_list'])
		
			if len(pin_list)<2: # if all pins are viewed
				request.session['viewed_list']=[]
				pin_list=pin_q
				
			pin_list=pin_list.order_by('-match')
			i=int(random.random()*len(pin_list)/5)
			j=int(random.random()*len(pin_list)/5)
			
			if i==j:
				if j==0:
					j+=1
				else:
					j-=1
								
			request.session.modified = True
			request.session['viewed_list'].append(pin_list[i].pin_id)
			request.session['viewed_list'].append(pin_list[j].pin_id)
			# Send the 2 picked pins 
			data = dumps({'status': 'OK', 'data': [pin_list[i], pin_list[j]]},cls=DjangoJSONEncoder)
			return HttpResponse(data, mimetype='application/json')
		
		else:
			# When there is no enough pin in the selcted category
			d={'status': 'ERR','data':'No pins in this category'}
			data = dumps(d,cls=DjangoJSONEncoder)
			return HttpResponse(data, mimetype='application/json')
	else:
		cat_list=CategoryModel.objects.all()
		return render(request,'map/vote.html',{'cat_list':cat_list})
	

def savematch(request):
	if request.is_ajax() and request.method =='POST':
		try:
			pin1_id=request.POST['pin1_id']
			pin2_id=request.POST['pin2_id']
			choice=request.POST['choice']
			
			pin1=PinModel.objects.get(pin_id=pin1_id)
			pin2=PinModel.objects.get(pin_id=pin2_id)
			
			pin1.score, pin2.score=Pin.getNewScore(pin1.score,pin2.score, pin1_id==choice)
			pin1.save()
			pin2.save()
			
			request.session.modified = True
			request.session['match_list'].append((pin1.pin_id, pin2.pin_id, choice))
	
			msg="OK"
			return HttpResponse(msg)
		
		except KeyError, PinModel.DoesNotExist:
			msg="Pin not found"
			return HttpResponse(msg)
	else:
		msg="Not a POST"
		return HttpResponse(msg)
	
def get_scoring(request):
	if request.method =='POST':
		user_id=request.POST['user_id']
		u=User(user_id)
		u.fetchScoring()
		user=u.saveDB()
		return HttpResponse(dumps(user,cls=DjangoJSONEncoder), mimetype='application/json')
		
	
	if request.method =='GET':
		user_id=request.GET['user_id']
		user=UserModel.objects.get(user_id=user_id)
		return HttpResponse(dumps(user,cls=DjangoJSONEncoder), mimetype='application/json')
			
		
	
