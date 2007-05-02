from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'extdjango.views.index'),
    (r'extform/$', 'extdjango.views.extform'),
    (r'extformsubmit/$', 'extdjango.views.extformsubmit'),
)

