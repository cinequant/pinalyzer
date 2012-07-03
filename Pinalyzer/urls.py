from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
         # Examples:
          # url(r'^cqsite/', include('cqsite.foo.urls')),
         
         # Uncomment the admin/doc line below to enable admin documentation:
         url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
         
         # Uncomment the next line to enable the admin:
         url(r'^admin/', include(admin.site.urls)),
         
         #pinalyzer
         url(r'^pinalyzer$', 'pinapp.views.index'),
         url(r'^$','map.views.home'),
         
          url(r'^ranking$','map.views.ranking'),
          url(r'^pinbattle$','map.views.vote'),
          url(r'^savematch$','map.views.savematch'),
          url(r'^score$','map.views.analytics'),
           url(r'^scoring','map.views.get_score'),
       #   url(r'^$', 'pinalyzer.pinapp.views.index'),
        
)
