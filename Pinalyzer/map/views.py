# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound, Http404  
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.utils.simplejson import dumps
from models import PinModel, CategoryModel, UserModel, UserStatModel, FbUserModel

import random, datetime
from user import User
from pin import Pin, Category
import scoring, fun
from django_json import MyEncoder

FB_INFO={'app_id':'198393166955666','app_namespace':'pinalyzer',}

def index(request):
	try:
		user_id=request.REQUEST['user_id']
	except KeyError:
		return render_to_response('map/index.html')
	
	u=User(user_id)  
	group_list=u.getFollowGroups() # all followers and following grouped by location			
	return render_to_response('map/index.html',{'group_list':dumps(group_list,cls=MyEncoder), 'fb_info':FB_INFO})

def invite(request):
	return render_to_response('map/invite.html', {'fb_info':FB_INFO})

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
				data = dumps(d,cls=MyEncoder)
				return HttpResponse(data, mimetype='application/json')
		except KeyError:
			ranking_q=PinModel.objects.all()
			
		# Personal ranking
		if request.GET['perso']== u'true':
			try:
				# Db-based personal ranking (only if the user is logged in with Facebook)
				fb_id=request.GET['fb_id']
				if fb_id=='null':
					raise KeyError
				fb_u=FbUserModel.objects.get(fb_id=fb_id)
				ranking_list=fb_u.pinpersomodel_set.all().order_by('-score')
				ranking_list=fun.group(lambda p: p.score, ranking_list)
				ranking_list=[[e.pin for e in sub] for sub in ranking_list ]
			except KeyError:
				# Cookie-based personal ranking
				match_list=request.session['match_list']
				score={}
				
				for t in match_list:
					pin1,pin2,choice=t
					score.setdefault(pin1,0)
					score.setdefault(pin2,0)
					score[pin1], score[pin2]=Pin.getNewScore(score[pin1],score[pin2], choice==pin1)
				
				ranking_list=list(ranking_q.filter(pin_id__in=score.keys()))
				ranking_list.sort(key=lambda pin: -score[pin.pin_id])
				ranking_list=fun.group(lambda p: p.score, ranking_list)
			data=dumps({'status':'OK','data':ranking_list},cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
		
		# Overall ranking
		if len(ranking_q)>0:
			ranking_q=ranking_q.order_by('-score')[:10]
			ranking_list=[]
			for pin in ranking_q:
				ranking_list.append(pin)
			
			ranking_list=fun.group(lambda p: p.score, ranking_list)
			data=dumps({'status':'OK','data':ranking_list},cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
		else:
			d={'status': 'ERR','data':'Error: No pins in this category'}
			data = dumps(d,cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
	else:
		raise Http404  

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
				data = dumps(d,cls=MyEncoder)
				return HttpResponse(data, mimetype='application/json')
					
		except KeyError:
			pin_q=PinModel.objects.all()
			
		if 'viewed_list' not in request.session :
			request.session['viewed_list']=[]
			
		if 'match_list' not in request.session:
			request.session['match_list']=[]
			
		if len(pin_q)>1:
			# exclude the pins already seen	
			pin_list=pin_q.exclude(pin_id__in=request.session['viewed_list'][-100:])
		
			if len(pin_list)<2 or len(request.session['viewed_list'])>100: # if all pins are viewed
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
			data = dumps({'status': 'OK', 'data': [pin_list[i], pin_list[j]]},cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
		
		else:
			# When there is no enough pin in the selcted category
			d={'status': 'ERR','data':'No pins in this category'}
			data = dumps(d,cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
	else:
		cat_list=CategoryModel.objects.all()
		try:
			pin_id=request.GET['pin_id']
			try:
				p=PinModel.objects.get(pin_id=pin_id)
				FB_INFO['meta']={'type':'pin', 'title': 'Pin', 'image': p.url, 'description': 'A pin from Pinterest.com', 'url':request.build_absolute_uri}
			except PinModel.DoesNotExist:
				pass
		except KeyError:
			pass
		return render(request,'map/vote.html',{'cat_list':cat_list,'fb_info':FB_INFO})
	

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
			
			try: # Save the match history if the user is logged with facebook
				fb_id=request.POST['fb_id']
				if fb_id=='null':
					raise KeyError
				fb_user =FbUserModel.objects.get_or_create(fb_id=fb_id)[0]
				pin1_perso= fb_user.pinpersomodel_set.get_or_create(pin=pin1)[0]
				pin2_perso= fb_user.pinpersomodel_set.get_or_create(pin=pin2)[0]
				pin1_perso.score, pin2_perso.score=Pin.getNewScore(pin1_perso.score,pin2_perso.score, pin1_id==choice)
				pin1_perso.save()
				pin2_perso.save()	
			except KeyError:
				pass
			
			request.session.modified = True
			request.session['match_list'].append((pin1.pin_id, pin2.pin_id, choice))
	
			msg="OK"
			return HttpResponse(msg)
		
		except KeyError, PinModel.DoesNotExist:
			msg="Pin not found"
			return HttpResponse(msg)
	else:
		raise Http404
	
	
def analytics(request):
	return render(request,'map/analytics.html',{'fb_info':FB_INFO})
	
def get_score(request):
	if request.is_ajax() and request.method =='POST':
		
		try:
			user_id=request.POST['user_id']
		except KeyError:
			return HttpResponse(dumps({'status':'ERR','data':'No user_id in post param'},cls=MyEncoder), mimetype='application/json')
		
		try:
			user=UserModel.objects.get(user_id=user_id)
			d=datetime.datetime.now()
			stat=user.userstatmodel_set.get(date__year=d.year, date__month=d.month, date__day=d.day)
		except (UserModel.DoesNotExist, UserStatModel.DoesNotExist) as e:
			u=User(user_id)
			try:
				u.fetchUser()
				u.fetchScoring()
				user=u.saveDB()
			except scoring.NotFound:
				return HttpResponse(dumps({'status':'ERR','data':'Wrong id, nobody have this id on pinterest'},cls=MyEncoder), mimetype='application/json')
			
			stat=user.latest_stat()
			
		score=stat.score()
		history= user.get_history()
		print history
		res={'status':'OK','data':{'user':user, 'stat': stat, 'score':score, 'history':history, 'last_history':history[-7:] },}
		return HttpResponse(dumps(res,cls=MyEncoder), mimetype='application/json')
	
	
def distribution(request):
	if request.is_ajax() and request.method =='GET':
		distrib=UserModel.get_distribution()
		res={'status':'OK','data':distrib}
		return HttpResponse(dumps(res,cls=MyEncoder), mimetype='application/json',)
	