#!/usr/bin/python3

import picamera
from picamera import PiCamera
from time import sleep
import time
import os
import datetime as dt

camera = PiCamera()
today = dt.date.today()
yesterday = today - dt.timedelta(days= 1)

camera.resolution = (1280,768)
camera.framerate = 25
camera.brightness = 57
camera.start_preview()
camera.annotate_background = picamera.Color('black')
camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
camera.annotate_text_size=24
camera.start_recording('/home/pi/Desktop/test/%s.h264' % today)
start = dt.datetime.now()


while (dt.datetime.now() - start).seconds < 28800:
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    camera.wait_recording(0.2)
sleep(0)
camera.stop_recording()
camera.stop_preview()
camera.close()

print("uploading")
print(dt.datetime.now())
os.system ('rclone copy /home/pi/Desktop/test gdmedia:RFIDVideos')
os.system('rm /home/pi/Desktop/test/%s.h264' % yesterday)

print("finished")
print(dt.datetime.now())
camera.stop_recording()
camera.stop_preview()

print("uploading")
print(dt.datetime.now())
os.system ('rclone copy /home/pi/Desktop/test gdmedia:RFIDVideos')
os.system('rm /home/pi/Desktop/test/%s.h264' % yesterday)

print("finished")
print(dt.datetime.now())