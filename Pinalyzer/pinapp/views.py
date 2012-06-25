# Create your views here.

from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render

import MySQLdb

#page d'accueil                                                                 
def index(request):
    return render(request,'pinapp/index.html')
