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
         url(r'^pinalyzer$', 'pinalyzer.pinapp.views.index'),
         
          url(r'^ranking$','pinalyzer.map.views.ranking'),
          url(r'^$','pinalyzer.map.views.vote'),
          url(r'^savematch$','pinalyzer.map.views.savematch'),
       #   url(r'^$', 'pinalyzer.pinapp.views.index'),
        
)
