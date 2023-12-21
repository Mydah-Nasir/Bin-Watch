# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

import cv2
import os
import threading
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
import supervision as sv
import numpy as np
from ultralytics import YOLO

rtsp_url = 'rtsp://admin:nust123456@192.168.0.118:554/Streaming/Channels/101'
webcam_url = 0

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
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

# Construct the path to best.pt dynamically
weights_path = os.path.join(BASE_DIR, 'static', 'assets', 'weights', 'best.pt')

model = YOLO(weights_path)  # Replace with the actual path to your YOLO model

byte_tracker = sv.ByteTrack()
annotator = sv.BoxAnnotator()
import math
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
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (640, 480))  # Adjust the resolution

            # Acquire lock and update the frame
            with self.lock:
                self.frame = frame_rgb

        self.cap.release()

# Initialize the video capture thread
video_thread = VideoCaptureThread(webcam_url)
video_thread.start()

@gzip.gzip_page
def video_feed(request):
    def generate():
        while True:
            with video_thread.lock:
                frame_rgb = video_thread.frame.copy()

            # Perform object detection on the frame
            annotated_frame = callback(frame_rgb, index=0)
            _, jpeg = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
def livefeed(request):
    return render(request, 'livefeed.html')
