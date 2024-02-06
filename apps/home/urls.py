# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import video_feed,livefeed


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('video_feed/', video_feed, name='video_feed'),
    path('livefeed/', livefeed, name='livefeed'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
