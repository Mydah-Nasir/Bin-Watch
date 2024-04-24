# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.template import loader
from .forms import AddUserForm,EditProfileForm, ReportUserForm, EditUserForm, VerifyReportForm
from django.urls import reverse
from bson import ObjectId
import cv2
import os
import threading
import math
import json
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
import supervision as sv
import numpy as np
from ultralytics import YOLO
from pymongo import MongoClient
from datetime import datetime
from .utils import CustomJSONEncoder
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa

client = MongoClient('localhost', 27017)
rtsp_url = 'rtsp://admin:nust123456@192.168.0.118:554/Streaming/Channels/101'
webcam_url = 0

prevPerson = [False]
prevTrash = [False]
person_count = [0]
trash_count = [0]
result = ['']
frame_buffer = []

dbname = client['BinWatch']
collection_name = dbname["ActivityLog"]
distance_collection = dbname["Distance"]
user_collection = dbname["User"]
report_collection = dbname["Report"]
#let's create two documents
activity_1 = {
    "activity_type" : "Littering",
    "camera_name" : "C2",
    "created_at": datetime.now()
}
activity_2 = {
    "activity_type" : "Not Littering",
    "camera_name" : "C2",
    "created_at": datetime.now()
}

#collection_name.insert_many([activity_1,activity_2])
logs_cursor = collection_name.find({}).limit(8)
logs_index = list(logs_cursor)
logs_cursor_all = collection_name.find({})
logs = list(logs_cursor_all)
users_cursor = user_collection.find({})
users = list(users_cursor)

@login_required(login_url="/login/")
def index(request):
    username = str(request.user)
    user_cursor = user_collection.find({"username": username})
    user_list = list(user_cursor)
    user = user_list[0]
    is_admin = user['is_admin']
    collection_name = dbname["ActivityLog"]
    trashposts_cursor_all = collection_name.find({}).sort('created_at', -1)
    trashposts = list(trashposts_cursor_all)
    logs_cursor = collection_name.find({})
    logs_index = list(logs_cursor)
    logs_cursor_all = collection_name.find({}).sort('created_at', -1)
    logs = list(logs_cursor_all)
    for trashpost in trashposts:
        trashpost['trashpost_id'] = str(trashpost['_id'])
        trashpost['img_url'] = trashpost['created_at'].strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'

    context = {'segment': 'index','trashposts':trashposts ,'logs':logs[:8] ,'logs_index': json.dumps(logs_index, cls=CustomJSONEncoder)}
    if(is_admin == "True"):
        return render(request, 'home/index.html',context)
    else:
        return render(request, 'home/trashposts.html',context)

def viewusers(request):
    user_collection = dbname["User"]
    users_cursor = user_collection.find({})
    users = list(users_cursor)
    for user in users:
        user['user_id'] = str(user['_id'])
    context = {'segment': 'viewusers','users':users}
    return render(request, 'home/viewusers.html',context)

def viewreports(request):
    report_collection = dbname["Report"]
    reports_cursor = report_collection.find({})
    reports = list(reports_cursor)
    for report in reports:
        report['report_id'] = str(report['_id'])
    context = {'segment': 'viewreports','reports':reports}
    return render(request, 'home/viewreports.html',context)

def activitylogs(request):
    collection_name = dbname["ActivityLog"]
    logs_cursor_all = collection_name.find({}).sort('created_at', -1)
    logs = list(logs_cursor_all)
    for log in logs:
        log['log_id'] = str(log['_id'])
    context = {}
    context['logs']=logs
    context['segment']='activitylogs'
    return render(request, 'home/activitylogs.html',context)

def trashposts(request):
    collection_name = dbname["ActivityLog"]
    trashposts_cursor_all = collection_name.find({}).sort('created_at', -1)
    trashposts = list(trashposts_cursor_all)
    for trashpost in trashposts:
        trashpost['trashpost_id'] = str(trashpost['_id'])
        trashpost['img_url'] = trashpost['created_at'].strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
    context = {}
    context['segment']='trashpost'
    context['trashposts']=trashposts
    return render(request, 'home/trashposts.html',context)

def deletelog(request, log_id):
    object_id = ObjectId(log_id)
    collection_name.delete_one({"_id": object_id})
    return redirect('activitylogs')

def deletereport(request, report_id):
    object_id = ObjectId(report_id)
    report_collection.delete_one({"_id": object_id})
    return redirect('viewreports')

def deleteuser(request, username):
    user_collection.delete_one({"username": username})
    return redirect('viewusers')

def sidebar(request):
    username = str(request.user)
    user_cursor = user_collection.find({"username": username})
    user_list = list(user_cursor)
    user = user_list[0]
    is_admin = user['is_admin']
    return { 'is_admin' : is_admin }

def adduser(request):
    msg = None
    success = False
    if request.method == "POST":
        form = AddUserForm(request.POST)
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
            is_admin = form.cleaned_data.get("is_admin")

            user = {
                'username':username,
                'qalamId':qalamId,
                'firstname':firstname,
                'lastname':lastname,
                'department':department,
                'batch':batch,
                'email':email,
                'is_admin':is_admin
            }
            user_collection.insert_many([user])

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = AddUserForm()

    return render(request, "home/adduser.html", {"segment":'adduser',"form": form, "msg": msg, "success": success})

def userprofile(request):
    msg = None
    success = False
    username = str(request.user)
    user_cursor = user_collection.find({"username": username})
    user_list = list(user_cursor)
    user = user_list[0]
    if request.method == "POST":
        form = EditProfileForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get("firstname")
            email = form.cleaned_data.get("email")
            qalamId = form.cleaned_data.get("qalamId")
            lastname = form.cleaned_data.get("lastname")
            department = form.cleaned_data.get("department")
            batch = form.cleaned_data.get("batch")
            

            # Construct the update query
            update_query = {
                "$set": {
                    "email":email,
                    "qalamId":qalamId,
                    "firstname": firstname,
                    "lastname": lastname,
                    "department": department,
                    "batch": batch,
                }
            }

            # Update the user document based on the username
            result = user_collection.update_one({"username": username}, update_query)

            if result.modified_count > 0:
                msg = 'User updated successfully.'
                success = True
            else:
                msg = 'User not found or update failed.'
                success = False

        else:
            msg = 'Form is not valid'
    else:
        form = EditProfileForm(initial=user)

    return render(request, "home/user.html", {"segment":'user',"username":username,"form": form, "msg": msg, "success": success})

def edituser(request,username):
    msg = None
    success = False
    user_cursor = user_collection.find({"username": username})
    user_list = list(user_cursor)
    user = user_list[0]
    if request.method == "POST":
        form = EditUserForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get("firstname")
            email = form.cleaned_data.get("email")
            qalamId = form.cleaned_data.get("qalamId")
            lastname = form.cleaned_data.get("lastname")
            department = form.cleaned_data.get("department")
            batch = form.cleaned_data.get("batch")
            is_admin = form.cleaned_data.get("is_admin")

            # Construct the update query
            update_query = {
                "$set": {
                    "email":email,
                    "qalamId":qalamId,
                    "firstname": firstname,
                    "lastname": lastname,
                    "department": department,
                    "batch": batch,
                    "is_admin": is_admin
                }
            }

            # Update the user document based on the username
            result = user_collection.update_one({"username": username}, update_query)

            if result.modified_count > 0:
                msg = 'User updated successfully.'
                success = True
            else:
                msg = 'User not found or update failed.'
                success = False

        else:
            msg = 'Form is not valid'
    else:
        form = EditUserForm(initial=user)

    return render(request, "home/edituser.html", {"segment":'user',"username":username,"form": form, "msg": msg, "success": success})
def generate_pdf(request):
    context = {
        'firstname': 'John',
        'lastname': 'Doe',
        'department': 'Engineering',
        'created_at': '2024-04-23 12:34:56',
        'camera_name': 'Camera 1',
        'img_url': 'example.jpg',
    }
    
    html = render_to_string('home/reportpdf.html', context)
    pdf = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=pdf)
    return pdf

def verifyreport(request,report_id):
    collection_name = dbname["ActivityLog"]
    msg = None
    success = False
    object_id = ObjectId(report_id)
    report_cursor = report_collection.find({"_id": object_id})
    report_list = list(report_cursor)
    report = report_list[0]
    firstname = report['firstname']
    lastname = report['lastname']
    department = report['department']
    post_id_str = report['post_id']
    post_id = ObjectId(post_id_str)
    post_cursor = collection_name.find({"_id": post_id})
    post_list = list(post_cursor)
    post = post_list[0]
    img_url = post['created_at'].strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
    camera_name = post['camera_name']
    created_at = post['created_at']
    if request.method == "POST":
        form = VerifyReportForm(request.POST)
        if form.is_valid():
            is_valid = form.cleaned_data.get("is_valid")

            # Construct the update query
            update_query = {
                "$set": {
                    "is_valid": is_valid
                }
            }

            # Update the report document based on the id
            result = report_collection.update_one({"_id": object_id}, update_query)

            if result.modified_count > 0:
                msg = 'Report updated successfully.'
                success = True
            else:
                msg = 'Report not found or update failed.'
                success = False

        else:
            msg = 'Form is not valid'
    else:
        form = VerifyReportForm(initial=report)

    return render(request, "home/verifyreport.html", {"segment":'report',"firstname":firstname,'lastname':lastname,'img_url':img_url,"department":department,'created_at':created_at,'camera_name':camera_name,"form": form, "msg": msg, "success": success})

@login_required(login_url="/login/")
def pages(request):
    context = {}
    context['logs']=logs
    context['users']=users
    username = str(request.user)
    user_collection = dbname["User"]
    user_cursor = user_collection.find({"username": username})
    user = list(user_cursor)
    context['user']=user[0]

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


# Get the base directory of your Django project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video_url = 'http://192.168.100.203:8080/video'

# Construct the path to best.pt dynamically
weights_path = os.path.join(BASE_DIR, 'static', 'assets', 'weights', 'best.pt')
video_path = os.path.join(BASE_DIR, 'static', 'assets', 'img', 'resulta.mp4')

model = YOLO(weights_path)  #actual path to YOLO model

byte_tracker = sv.ByteTrack()
annotator = sv.BoxAnnotator()

def add_activty_log(result):
    if result[0] == '':
        return
    elif result[0]=='Littering' or result[0]=='Not Littering':
        activity = ActivityLog.objects.create(
        activity_type = result[0],
        camera_name = "C2",
        created_at = datetime.now()
        )
        # collection_name = dbname["ActivityLog"]
        # collection_name.insert_many([activity])
    

import math
def calculate_distance(box1, box2):
    # Extract coordinates of the centers
    center1_x, center1_y = box1[0] + box1[2] / 2, box1[1] + box1[3] / 2
    center2_x, center2_y = box2[0] + box2[2] / 2, box2[1] + box2[3] / 2

    # Calculate Euclidean distance
    distance = math.sqrt((center1_x - center2_x)*2 + (center1_y - center2_y)*2)
    print(distance)
    return distance

def is_overlap(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    print("Box1: ",x1, y1, w1, h1)
    print("Box2: ",x2, y2, w2, h2)
    # Check for overlap along the x-axis
    if x1 < x2 + w2 and x1 + w1 > x2:
        # Check for overlap along the y-axis
        if y1 < y2 + h2 and y1 + h1 > y2:
            print('Overlap')
            return True  # Bounding boxes overlap
    print('No overlap')
    return False  # Bounding boxes do not overlap

def save_frame(frame, activity):
    if activity == 'Littering':
        created_at = datetime.now()
        activity = {
        "activity_type" : 'Littering',
        "camera_name" : "Hostel",
        "created_at": datetime.now(),
        }
        collection_name = dbname["ActivityLog"]
        collection_name.insert_many([activity])
        # Specify the directory where you want to save the frame
        save_dir = os.path.join(os.getcwd(), "apps", "static", "assets", "littering_images")
        os.makedirs(save_dir, exist_ok=True)  # Create the directory if it doesn't exist
        # Save the frame in the specified directory
        filename = created_at.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        save_path = os.path.join(save_dir, filename)
        cv2.imwrite(save_path, frame)
    elif activity == 'Not Littering':
        created_at = datetime.now()
        activity = {
        "activity_type" : 'Not Littering',
        "camera_name" : "Hostel",
        "created_at": datetime.now(),
        }
        collection_name = dbname["ActivityLog"]
        collection_name.insert_many([activity])


def process_frame(frame: np.ndarray, prevPerson, prevTrash, person_count, trash_count, result,frame_buffer):
    detections = model(frame)[0]
    is_trash = False
    is_person = False
    result[0]=''

    # Create a buffer to store frames
    if len(frame_buffer) >= 5:
        frame_buffer.pop(0)  # Remove the oldest frame if buffer is full
    frame_buffer.append(frame.copy())

    for detection in detections:
        class_number = int(detection.boxes.cls[0].item())
        class_name = detection.names[class_number]
        print(class_name)
        confidence = detection.boxes.conf.item()
        x, y, w, h = detection.boxes.xywh[0].cpu().numpy()

        # Example: Check if the detected object is "Trash" or "TrashCan"
        if class_name == "Trash":
            trash_box = (x, y, w, h)
            is_trash = True
        elif class_name == "TrashCan":
            trashcan_box = (x, y, w, h)
        elif class_name == "Person":
            person_box = (x, y, w, h)
            is_person = True

    if is_person and is_trash:
        trash_count[0] = trash_count[0] + 1
        prevTrash[0] = True
        if not is_overlap(person_box,trash_box):
            prevPerson[0] = True
            person_count[0] = person_count[0] + 1
            prevTrash[0] = True
    elif is_trash:
        if prevPerson[0] and person_count[0]>3:
            person_count[0] = 0
            result[0] = 'Littering'
            #add_activty_log(result[0])
            save_frame(frame_buffer[0],'Littering')
            print(result[0])
    elif is_person:
        print(prevTrash[0],trash_count[0])
        if prevTrash[0]  and trash_count[0]>5:
            trash_count[0] = 0
            result[0] = 'Not Littering'
            #add_activty_log('Not Littering')
            save_frame(frame_buffer[0],'Not Littering')
            print(result[0])

def callback(frame: np.ndarray, index: int) -> np.ndarray:
    # Perform object detection using Ultralytics YOLO model
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = byte_tracker.update_with_detections(detections)
    labels = [
        f"#{tracker_id} {model.names[class_id]} {confidence:0.2f}"
        for _, _, confidence, class_id, tracker_id
        in detections
    ]

    return annotator.annotate(scene=frame.copy(), detections=detections, labels=labels)
# Move the video capture logic into a separate thread
class VideoCaptureThread(threading.Thread):
    def __init__(self, rtsp_url):
        super(VideoCaptureThread, self).__init__()
        self.cap = cv2.VideoCapture(rtsp_url)
        self.frame = None
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Convert the frame to RGB and resize
            #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame, (640, 480))  # Adjust the resolution

            # Acquire lock and update the frame
            with self.lock:
                self.frame = frame_rgb

        self.cap.release()

# Initialize the video capture thread
video_thread = VideoCaptureThread(video_url)
video_thread.start()

@gzip.gzip_page
def video_feed(request):
    def generate():
        while True:
            with video_thread.lock:
                frame_rgb = video_thread.frame.copy()
            process_frame(frame_rgb,prevPerson, prevTrash, person_count, trash_count, result,frame_buffer)
            #add_activty_log(result)
            # Perform object detection on the frame
            annotated_frame = callback(frame_rgb, index=0)
            _, jpeg = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

def video_path(request):
    # Initialize the video capture
    cap = cv2.VideoCapture(video_path)  # Replace "your_video_file.mp4" with the path to your video file
    
    def generate():
        while True:
            # Read a frame from the video capture
            ret, frame = cap.read()
            if not ret:
                break

            # Encode the frame as JPEG
            _, jpeg = cv2.imencode('.jpg', frame)

            # Yield the frame as part of the video stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    # Return a StreamingHttpResponse with the generated frames
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

def livefeed(request):
    context = {}
    context['logs']=logs
    context['segment']='livefeed'
    return render(request, 'livefeed.html',context)

def reportuser(request,post_id):
    msg = None
    success = False

    if request.method == "POST":
        form = ReportUserForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get("firstname")
            lastname = form.cleaned_data.get("lastname")
            department = form.cleaned_data.get("department")
            username = form.cleaned_data.get("username")
            
            report = {
                'firstname':firstname,
                'lastname':lastname,
                'department':department,
                'is_valid':'False',
                'post_id':post_id,
                'username': username,
            }
            report_collection.insert_many([report])

            msg = 'Report created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = ReportUserForm()

    return render(request, "home/reportuser.html", {"form": form, "msg": msg, "success": success})
