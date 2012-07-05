# Copyright 2012, RespLab. All rights reserved.

from django.conf.urls.defaults import patterns, url
from config.authentification import stop_anon
from application.views import my_apps, ConfigView

urlpatterns = patterns('',
    url(r'^me$', stop_anon(my_apps), name='application_me'),
    url(r'^config/$', stop_anon(ConfigView.as_view()), name="get_config"),
    url(r'^config/(?P<id>\d+)', stop_anon(ConfigView.as_view()), name="get_config"),
)
