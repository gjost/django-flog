from django.conf.urls.defaults import *

urlpatterns = patterns('flog.views',
    (r'^(?P<yyyy>\d{4})/(?P<mm>\d{1,2})/(?P<dd>\d{1,2})/$', 'day'),
    (r'^$', 'index'),
)
