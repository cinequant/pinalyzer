# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound, Http404  
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.utils.simplejson import dumps
from django.db.models import Count,Q
from models import PinModel, CategoryModel, UserModel, UserStatModel, SocialUserModel, QuizzVoteModel, MatchModel

import random, datetime, calendar,  os, time
from threading import Thread, Lock
from user import User
from pin import Pin
from category import Category
import scoring, fun, user
from django_json import MyEncoder
from userheader import  NotFound

FB_INFO = {'app_id':'198393166955666', 'app_namespace':'pinalyzertest', }

def index(request):
	try:
		user_id = request.REQUEST['user_id']
	except KeyError:
		return render_to_response('map/index.html')
	
	u = User(user_id)  
	group_list = u.getFollowGroups() # all followers and following grouped by location			
	return render_to_response('map/index.html', {'group_list':dumps(group_list, cls=MyEncoder), 'fb_info':FB_INFO})

def about(request):
	return render_to_response('map/about.html', {'fb_info':FB_INFO})

def invite(request):
	return render_to_response('map/invite.html', {'fb_info':FB_INFO})

def ranking(request):
	if request.is_ajax() and request.method == 'GET':
		
		try:
			cat = request.GET['category']
			try:
				if cat == 'all':
					ranking_q = PinModel.objects.all()
				else:
					cat_model = CategoryModel.objects.get(category_id=cat)
					ranking_q = cat_model.pinmodel_set.all()
			except CategoryModel.DoesNotExist:
				d = {'status': 'ERR', 'data':'This category does not exist on the database '}
				data = dumps(d, cls=MyEncoder)
				return HttpResponse(data, mimetype='application/json')
		except KeyError:
			ranking_q = PinModel.objects.all()
			
		# Personal ranking
		if request.GET['perso'] == u'true':
			info_open_graph = []
			try:
				# Db-based personal ranking (only if the user is logged in with Facebook)
				fb_id = request.GET['fb_id']
				#access_token=request.GET['access_token']
				if fb_id == 'null':
					raise KeyError
				fb_u = SocialUserModel.objects.get_or_create(social_id=fb_id, net_name="facebook")[0]
				pin_id_list = [p.pin_id for p in ranking_q]
				pin_list = fb_u.pinpersomodel_set.order_by('-score').filter(pin__pin_id__in=pin_id_list)
				
				ranking_list = fun.group(lambda p: p.score, pin_list)
				ranking_list = [[e.pin for e in sub] for sub in ranking_list ]

				if ranking_list:
					nb=3 # Number of pin to post on facebook
					if len(ranking_list[0])>3:
						to_post=random.sample(ranking_list[0],nb)
					else:
						to_post=pin_list[:3]
					for p in to_post:
						p_url = 'http://'+request.get_host() + '/pin?pin_id=' + p.pin_id
						info_open_graph.append({'fb_id':fb_id, 'action':'vote for', 'obj':'pin', 'obj_url':p_url})
			except KeyError:
				# Cookie-based personal ranking
				match_list = request.session['match_list']
				score = {}
				
				for t in match_list:
					pin1, pin2, choice = t
					score.setdefault(pin1, 0)
					score.setdefault(pin2, 0)
					score[pin1], score[pin2] = Pin.getNewScore(score[pin1], score[pin2], choice == pin1)
				
				ranking_list = list(ranking_q.filter(pin_id__in=score.keys()))
				ranking_list.sort(key=lambda pin:-score[pin.pin_id])
				ranking_list = fun.group(lambda p: p.score, ranking_list)
			
			if len(ranking_list) > 0:
				data = dumps({'status':'OK', 'data':{'ranking_list':ranking_list, 'info_open_graph':info_open_graph}}, cls=MyEncoder)
				return HttpResponse(data, mimetype='application/json')
			else:
				d = {'status': 'ERR', 'data':'No pins in this category'}
				data = dumps(d, cls=MyEncoder)
				return HttpResponse(data, mimetype='application/json')
			
		# Overall ranking
		if len(ranking_q) > 0:
			ranking_q = ranking_q.order_by('-score')[:10]
			ranking_list = []
			for pin in ranking_q:
				ranking_list.append(pin)
			
			ranking_list = fun.group(lambda p: p.score, ranking_list)
			data = dumps({'status':'OK', 'data':{'ranking_list':ranking_list}}, cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
		else:
			d = {'status': 'ERR', 'data':'Error: No pins in this category'}
			data = dumps(d, cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
	else:
		raise Http404  

def vote(request):
	if request.is_ajax() and request.method == 'GET':
		
		# Select all pins in a given category
		try:
			cat = request.GET['category']
			try:
				if cat == 'all':
					pin_q = PinModel.objects.all()
				else:
					cat_model = CategoryModel.objects.get(category_id=cat)
					pin_q = cat_model.pinmodel_set.all()
			except CategoryModel.DoesNotExist:
				d = {'status': 'ERR', 'data':'This category does not exist'}
				data = dumps(d, cls=MyEncoder)
				return HttpResponse(data, mimetype='application/json')
					
		except KeyError:
			pin_q = PinModel.objects.all()
			
		if 'viewed_list' not in request.session :
			request.session['viewed_list'] = []
			
		if 'match_list' not in request.session:
			request.session['match_list'] = []
			
		if len(pin_q) > 1:
			# exclude the pins already seen	
			pin_list = pin_q.exclude(pin_id__in=request.session['viewed_list'][-100:])
		
			if len(pin_list) < 2 or len(request.session['viewed_list']) > 100: # if all pins are viewed
				request.session['viewed_list'] = []
				pin_list = pin_q
				
			pin_list = pin_list.order_by('-match')
			i = int(random.random() * len(pin_list) / 5)
			j = int(random.random() * len(pin_list) / 5)
			
			if i == j:
				if j == 0:
					j += 1
				else:
					j -= 1
								
			request.session.modified = True
			request.session['viewed_list'].append(pin_list[i].pin_id)
			request.session['viewed_list'].append(pin_list[j].pin_id)
			# Send the 2 picked pins 
			data = dumps({'status': 'OK', 'data': [pin_list[i], pin_list[j]]}, cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
		
		else:
			# When there is no enough pin in the selcted category
			d = {'status': 'ERR', 'data':'No pins in this category'}
			data = dumps(d, cls=MyEncoder)
			return HttpResponse(data, mimetype='application/json')
	else:
		cat_list = CategoryModel.objects.all()
		return render(request, 'map/vote.html', {'cat_list':cat_list, 'fb_info':FB_INFO})
	

def savematch(request):
	if request.is_ajax() and request.method == 'POST':
		try:
			pin1_id = request.POST['pin1_id']
			pin2_id = request.POST['pin2_id']
			choice = request.POST['choice']
			
			pin1 = PinModel.objects.get(pin_id=pin1_id)
			pin2 = PinModel.objects.get(pin_id=pin2_id)
			
			pin1.score, pin2.score = Pin.getNewScore(pin1.score, pin2.score, pin1_id == choice)
			pin1.save()
			pin2.save()
			
			try: # Save the match history if the user is logged with facebook
				fb_id = request.POST['fb_id']
				if fb_id == 'null':
					raise KeyError
				fb_user = SocialUserModel.objects.get_or_create(social_id=fb_id, net_name="facebook")[0]
				pin1_perso = fb_user.pinpersomodel_set.get_or_create(pin=pin1)[0]
				pin2_perso = fb_user.pinpersomodel_set.get_or_create(pin=pin2)[0]
				pin1_perso.score, pin2_perso.score = Pin.getNewScore(pin1_perso.score, pin2_perso.score, pin1_id == choice)
				pin1_perso.save()
				pin2_perso.save()	
			except KeyError:
				pass
			
			request.session.modified = True
			request.session['match_list'].append((pin1.pin_id, pin2.pin_id, choice))
	
			msg = "OK"
			return HttpResponse(msg)
		
		except KeyError, PinModel.DoesNotExist:
			msg = "Pin not found"
			return HttpResponse(msg)
	else:
		raise Http404
	
	
def analytics(request):
	try:
		user_id = request.GET['user']
		user = UserModel.objects.get(user_id=user_id)
		d=datetime.datetime.now()
		FB_INFO['meta'] = {'type':'person',
						'title': user.name,
						'image':'http://'+request.get_host()+'/score_img?user_id='+user_id+'&date='+str(d.day)+'_'+str(d.month)+'_'+str(d.year),
						'description': user.name + '\'s pinterest score is '+str(round(user.latest_stat().score(),1))+' on pinalyzer.com',
						'url':request.build_absolute_uri(),
						}
	except (KeyError, UserModel.DoesNotExist):
		pass
	return render(request, 'map/analytics.html', {'fb_info':FB_INFO})
	
def get_score(request):
	if request.is_ajax() and request.method == 'POST':
		try:
			user_id = request.POST['user_id']
			
		except KeyError:
			return HttpResponse(dumps({'status':'ERR', 'data':'No user_id in post param'}, cls=MyEncoder), mimetype='application/json')
		
		try:
			user = UserModel.objects.get(user_id=user_id)
			d = datetime.datetime.now()
			stat = user.userstatmodel_set.get(date__year=d.year, date__month=d.month, date__day=d.day)
		except (UserModel.DoesNotExist,UserStatModel.DoesNotExist):
			u = User(user_id)
			try:
				u.fetchUser()
				u.fetchScoring()
				user = u.saveDB()
			except scoring.NotFound:
				return HttpResponse(dumps({'status':'ERR', 'data':'Wrong id, nobody have this id on pinterest'}, cls=MyEncoder), mimetype='application/json')

		info_open_graph = []
		try:
			fb_id = request.POST['fb_id']
			if fb_id == 'null':
				raise KeyError
			fb_u = SocialUserModel.objects.get_or_create(social_id=fb_id, net_name="facebook")[0]
			d=datetime.datetime.now()
			info_open_graph.append({'fb_id':fb_id, 'action':'rate', 'obj':'person', 'obj_url':'http://'+request.get_host()+'/score?user='+user.user_id+'&date='+str(d.day)+'_'+str(d.month)+'_'+str(d.year)})
		except KeyError:
			pass
		
		stat_hist=user.userstatmodel_set.all().order_by('date')
		
		
		followers_hist=[]
		following_hist=[]
		pin_hist=[]
		liked_hist=[]
		board_hist=[]
		score_hist=[]
		repin_hist=[]
		comment_hist=[]
		like_hist=[]

		for s in stat_hist:
			epoch=time.mktime(s.date.timetuple())*1000
			followers_hist.append([epoch, s.nb_followers])
			following_hist.append([epoch, s.nb_following])
			pin_hist.append([epoch, s.nb_pin])
			liked_hist.append([epoch, s.nb_liked])
			board_hist.append([epoch, s.nb_board])
			score_hist.append([epoch, s.score()])
			repin_hist.append([epoch, s.nb_repin])
			comment_hist.append([epoch, s.nb_comment])
			like_hist.append([epoch, s.nb_like])
			
		all_hist={'followers_hist':followers_hist,
					'following_hist':following_hist,
					'pin_hist':pin_hist,
					'liked_hist':liked_hist,
					'board_hist':board_hist,
					'score_hist':score_hist,
					'repin_hist':repin_hist,
					'comment_hist':comment_hist,
					'like_hist':like_hist,
		}
		res = {'status':'OK', 'data':{'user':user, 
									'all_hist':all_hist,
									'info_open_graph':info_open_graph }, }
		return HttpResponse(dumps(res, cls=MyEncoder), mimetype='application/json')
		
def score_img(request):
	try:
		user_id = request.GET['user_id']
		user = UserModel.objects.get(user_id=user_id)
	except KeyError, UserModel.DoesNotExist:
		raise Http404
	img=fun.scoreToImg(round(user.latest_stat().score(),1),user.name)
	response = HttpResponse(mimetype="image/png")
	img.save(response, "PNG")
	return response

def distribution(request):
	print 'hey'
	distrib = UserModel.get_distribution()
	res = {'status':'OK', 'data':distrib}
	return HttpResponse(dumps(res, cls=MyEncoder), mimetype='application/json',)
	
def pin(request):
	try:
		pin_id = request.GET['pin_id']
	except KeyError:
		return render(request, 'map/pin.html', {'fb_info':FB_INFO})

	try:
		p = PinModel.objects.get(pin_id=pin_id)
	except PinModel.DoesNotExist:
		return render(request, 'map/pin.html', {'fb_info':FB_INFO})
	
	FB_INFO['meta'] = {'type':'pin',
					'title': 'a ' + p.pinner_name + '\'s pin ',
					'image': p.url,
					'description': p.category.category_name,
					'url':request.build_absolute_uri(),
					}
	return render(request, 'map/pin.html', {'fb_info':FB_INFO,'pin':p})

def suggestion(request):
	if request.is_ajax() and request.method=='GET':
		try:
			user_id = request.GET['user_id']
		except KeyError:
			return HttpResponse(dumps({'status':'ERR', 'data':'No user id'}, cls=MyEncoder), mimetype='application/json')
		
		u=User(user_id)
		
		try:
			pin_list=u.getToRepin(10)
			try:
				UserModel.objects.get(user_id=user_id)
			except UserModel.DoesNotExist:
				u.saveDB()
		except NotFound:
			return HttpResponse(dumps({'status':'ERR', 'data':'Wrong name, nobody have this name on pinterest'}, cls=MyEncoder), mimetype='application/json')
		
		if not pin_list:
			pin_list=[Pin.modelToPin(p) for p in random.sample(PinModel.objects.all(),10)]
		res = {'status':'OK', 'data':{'pin_list':pin_list,'user':u}, }
		return HttpResponse(dumps(res, cls=MyEncoder), mimetype='application/json')
	else:
		return render_to_response('map/suggestion.html', {'fb_info':FB_INFO,})
	
def quizz(request):	
	if request.is_ajax() and request.method=='GET':
		try:
			user_id = request.GET['user_id']
		except KeyError:
			return HttpResponse(dumps({'status':'ERR', 'data':'No user id'}, cls=MyEncoder), mimetype='application/json')
		
		try:
			user_m=UserModel.objects.get(user_id=user_id)
		except UserModel.DoesNotExist:
			x=User(user_id)
			x.fetchUser()
			user_m=x.saveDB()
	
		user_m.quizzvotemodel_set.all().delete();
		ref_list=[[x.pin1,x.pin2,True] for x in list(MatchModel.objects.all()[:5])]
		s=random.sample(list(PinModel.objects.all()),10)
		rand_list=[[s[i],s[i+1],False] for i in range(0,len(s),2)]
		match_list=fun.shuffle(ref_list+rand_list);	
		res = {'status':'OK', 'data':{'match_list':match_list,}, }
		return HttpResponse(dumps(res, cls=MyEncoder), mimetype='application/json')
	else:
		try:
			user_id = request.GET['user_id']
		except KeyError:
			raise Http404
		return render_to_response('map/quizz.html', {'fb_info':FB_INFO,'user_id':user_id})

def savequizzvote(request):
	if request.is_ajax() and request.method == 'POST':
		try:
			choice = request.POST['choice']
			user_id= request.POST['user_id']
			user = UserModel.objects.get(user_id=user_id)
			voted_pin = PinModel.objects.get(pin_id=choice)
			QuizzVoteModel.objects.create(user=user, voted_pin=voted_pin)
			return HttpResponse(dumps({'status':'OK','data':''}, cls=MyEncoder), mimetype='application/json')
		
		except KeyError, PinModel.DoesNotExist:
			return HttpResponse(dumps({'status':'ERR','data':'Pin or User not found'}, cls=MyEncoder), mimetype='application/json')
	else:
		raise Http404
	
def quizzresult(request):
	print request.method
	if request.is_ajax() and request.method=='GET':
		try:
			user_id = request.GET['user_id']
		except KeyError:
			return HttpResponse(dumps({'status':'ERR', 'data':'No user id'}, cls=MyEncoder), mimetype='application/json')
		
		print 'trouver db'
		user = UserModel.objects.get(user_id=user_id)
		participant =  UserModel.objects.annotate(vote_count=Count('quizzvotemodel')).filter(Q(vote_count__gte=1) & ~Q(user_id=user_id))
		u = User(user_id)
		other = []
		if len(participant) > 0:
			u_pins = [v.voted_pin.pin_id for v in user.quizzvotemodel_set.all()]
			for x in participant:
				x_pins = [v.voted_pin.pin_id for v in x.quizzvotemodel_set.all()]
				print x
				other.append([x, len(set(u_pins) & set(x_pins))])
			other.sort(key=lambda x:x[1])
			print other
			other=other[-2:]
			alikes = [User.modelToUser(x[0]) for x in other]
			u.fetchFollowing(1)
		else:
			alikes = u.getAlikes()[-2:]
		
		to_follow = u.getToFollow(alikes)[-4:]
		"""
		thread_list=[]
		for f in to_follow:
			print f
			def task(f):
				f.fetchUser()
			t=Thread(target=task, args=(f,))
			thread_list.append(t)
			
		for t in thread_list:
			t.start();
		for t in thread_list:
			t.join();
		"""
		
		res = {'status':'OK', 'data':{'participant': other, 'alikes':alikes,'to_follow':to_follow}}
		return HttpResponse(dumps(res, cls=MyEncoder), mimetype='application/json')
			