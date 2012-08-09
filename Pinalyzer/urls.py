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
                        
                        url(r'^$', 'map.views.suggestion'),
                        url(r'^invite$', 'map.views.invite'),
                        url(r'^score$', 'map.views.score_page'),
                        url(r'^analytics$', 'map.views.analytics'),
                        
                        url(r'^ranking$', 'map.views.ranking'),
                        url(r'^savematch$', 'map.views.savematch'),
                        url(r'^distribution$', 'map.views.distribution'),
                        url(r'^scoring$', 'map.views.get_score'),
                        url(r'^score_img$', 'map.views.score_img'),
                        url(r'^pin$', 'map.views.pin'),
                        url(r'^about$', 'map.views.about'),
                        url(r'^pinbattle', 'map.views.vote'),
                        url(r'^get_pin_suggestion$', 'map.views.get_pin_suggestion'),
                        url(r'^quizz$', 'map.views.quizz'),
                        url(r'^savequizzvote$', 'map.views.savequizzvote'),
                        url(r'^quizzresult$', 'map.views.quizzresult'),
                         url(r'^testuser', 'map.views.testuser'),
                        #   url(r'^$', 'pinalyzer.pinapp.views.index'),       
)



