from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pinalyzer.views.home', name='home'),
    # url(r'^pinalyzer/', include('pinalyzer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^map/index/$','map.views.index' ),
    url(r'^map/pinmatch/ranking$','map.views.ranking'),
    url(r'^map/pinmatch/vote$','map.views.vote'),
)
