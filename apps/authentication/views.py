# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import ssl
import certifi

# Create SSL context with certificate verification disabled
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


uri = "mongodb+srv://alina11nasir:lK9ZrZOvxnYGIreb@binwatch.xyrfu00.mongodb.net/?retryWrites=true&w=majority&appName=BinWatch"
# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where()) 
dbname = client['BinWatch']
collection_name = dbname["User"]

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            qalamId = form.cleaned_data.get("qalamId")
            firstname = form.cleaned_data.get("firstname")
            lastname = form.cleaned_data.get("lastname")
            department = form.cleaned_data.get("department")
            batch = form.cleaned_data.get("batch")
            email = form.cleaned_data.get("email")
            is_admin = "False"

            user = {
                'username':username,
                'qalamId':qalamId,
                'firstname':firstname,
                'lastname':lastname,
                'department':department,
                'batch':batch,
                'email':email,
                'is_admin': is_admin
            }
            collection_name.insert_many([user])

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

