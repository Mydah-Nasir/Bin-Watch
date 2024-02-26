# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import video_feed,livefeed,adduser,viewusers,userprofile,reportuser,trashpost,activitylogs,trashposts


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('video_feed/', video_feed, name='video_feed'),
    path('reportuser/<str:post_id>/', reportuser, name='report_user'),
    path('livefeed/', livefeed, name='livefeed'),
    path('trashpost/', trashpost, name='trashpost'),
    path('adduser/', adduser, name='adduser'),
    path('viewusers/',viewusers,name='viewusers'),
    path('activitylogs/',activitylogs,name='activitylogs'),
    path('trashposts/',trashposts,name='trashposts'),
    path('user/',userprofile,name='user'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
