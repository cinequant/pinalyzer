# -*- coding: utf-8 -*-
import os, sys

# On ajoute le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pinalyzer.settings'

# On ajoute le path vers les bibliothèques
#sys.path.append('/srv/cqlib')

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
