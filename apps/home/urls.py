# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import video_feed,livefeed,adduser,viewusers,userprofile,reportuser,activitylogs,deletelog,edituser,deleteuser,trashposts,viewreports, deletereport, verifyreport


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('video_feed/', video_feed, name='video_feed'),
    path('reportuser/<str:post_id>/', reportuser, name='report_user'),
    path('livefeed/', livefeed, name='livefeed'),
    path('adduser/', adduser, name='adduser'),
    path('viewusers/',viewusers,name='viewusers'),
    path('viewreports/',viewreports,name='viewreports'),
    path('activitylogs/',activitylogs,name='activitylogs'),
    path('trashposts/',trashposts,name='trashposts'),
    path('user/',userprofile,name='user'),
    path('delete-log/<str:log_id>/', deletelog, name='deletelog'),
    path('deleteuser/<str:username>/',deleteuser , name='deleteuser'),
    path('deletereport/<str:report_id>/', deletereport, name='deletereport'),
    path('edituser/<str:username>/', edituser, name='edituser'),
    path('verifyreport/<str:report_id>/', verifyreport, name='verifyreport'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
