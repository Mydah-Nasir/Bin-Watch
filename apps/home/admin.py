# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import ActivityLog
# Register your models here.

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'camera_name', 'created_at')
    list_filter = ('activity_type', 'camera_name', 'created_at')
    search_fields = ('activity_type', 'camera_name', 'created_at')