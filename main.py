import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import utils
from Motors import Motor
motor = Motor(32, 16, 18, 12, 29, 31)
curvelist = []
avgVal = 10
initialTrackVals = [107, 99, 25, 240]
utils.initializeTrackbars(initialTrackVals)
def get_lane_curve(img, display=0):
        imgcopy = img.copy()
        imgResult = img.copy()
    #### STEP 1 ####
        thresholded = utils.thresholding(img)



    #### STEP 2 ####
        hT, wT, c = img.shape
        points = utils.valTrackbars()
        imgWarp = utils.warpImg(thresholded, points, wT, hT)
    #### STEP 3 ####
        imgWarpPoints = utils.drawPoints(imgcopy, points)
        basepoint, imgHisto = utils.getHistogram(imgWarp, minPer=0.5) # full path

        midpoint, imgHistogram = utils.getHistogram(imgWarp, minPer=0.5, region=4) # one-fourth

        curveRaw = basepoint - midpoint
    #### step 4 ####
        curvelist.append(curveRaw)
        if (len(curvelist) > avgVal):
            curvelist.pop(0)
            curve = int(sum(curvelist) / len(curvelist))
    #### STEP 5 ####
        if display != 0:
            imgInvWarp = utils.warpImg(imgWarp, points, wT, hT, inv=True)
            imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
            imgInvWarp[0:hT // 3, 0:wT] = 0, 0, 0
            imgLaneColor = np.zeros_like(img)
            imgLaneColor[:] = 0, 255, 0
            imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)


            imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
            midY = 450
            cv2.putText(imgResult, (str(basepoint) + " " + str(curve) + " " + str(midpoint)), (wT // 2 -
            80, 85),
            cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
            cv2.line(imgResult, (wT // 2, midY), (wT // 2 + (curve * 3), midY), (255, 0, 255), 5)
            cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY - 25), (wT // 2 + (curve * 3), midY +
            25), (0, 255, 0), 5)
            for x in range(-30, 30):
            w = wT // 20
            cv2.line(imgResult, (w * x + int(curve // 50), midY - 10),
            (w * x + int(curve // 50), midY + 10), (0, 0, 255), 2)
    # fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
    # cv2.putText(imgResult, 'FPS ' + str(int(fps)), (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (230, 50, 50), 3)
    if display == 2:
        imgStacked = utils.stackImages(0.7, ([img, imgWarpPoints, imgWarp],
    [imgHisto, imgLaneColor, imgResult]))
    cv2.imshow('ImageStack', imgStacked)
    elif display == 1:
    cv2.imshow('Resutlt', imgResult)
    #### NORMALIZATION ####
    curve = curve / 100
    if curve > 1:
    curve = 1


    if curve < -1:
        curve = -1
        return curve, basepoint, midpoint
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (480, 240)
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=(480, 240))
    # allow the camera to warmup
    sleep(0.1)
    i = 0
    initialTrackVals = [107, 99, 25, 240]
    utils.initializeTrackbars(initialTrackVals)
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        flipped = cv2.flip(image, -1)
        curveVal, basePoint, midPoint = get_lane_curve(flipped, display=1)
        sen = 2 # SENSITIVITY
        maxVAl = 0.3 # MAX SPEED
        default_speed = 0.20
        if curveVal > maxVAl: curveVal = maxVAl
        if curveVal < -maxVAl: curveVal = -maxVAl


        # if curveVal >= 0.07:
        # curveVal -= 0.03
        #
        # if curveVal <= -0.07:
        # curveVal += 0.03
        #
        # if basePoint < 160:
        # if abs(basePoint - midPoint) < 7:
        # curveVal -= 0.04
        #
        # if basePoint > 330:
        # if abs(basePoint - midPoint) < 7:
        # curveVal += 0.04
        if(basePoint >= 200) & (basePoint <= 280):
            if curveVal >= 0.04:
                curveVal -= curveVal/2
            elif curveVal <= -0.04:
                curveVal += curveVal/2
            
        if (curveVal <= -0.02) & (curveVal >= -0.04):
            if (basePoint < 200) & (basePoint > 150):
                curveVal -= 0.02
            elif basePoint < 150:
                curveVal -= 0.02
            else:
                curveVal = curveVal

        if (curveVal <= -0.05) & (curveVal >= -0.07):
            if basePoint < 150:
                curveVal -= 0.02
            elif (basePoint > 150) & (basePoint < 240):
                curveVal -= 0.01
            else:
                curveVal = curveVal

        if (curveVal >= 0.02) & (curveVal <= 0.04):
            if basePoint > 240:
                curveVal += 0.02
            else:
                curveVal = curveVal

        if (curveVal >= 0.05) & (curveVal <= 0.07):
            if basePoint > 200:
                curveVal += 0.02
            else:
                curveVal = curveVal

        if (curveVal < 0.01) & (curveVal > -0.01):
            curveVal = 0
            
        motor.move(default_speed, curveVal * sen, 0.05)

        # cv2.waitKey(0)
        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break