import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
def thresholding(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_hue = np.array([0, 0, 155], dtype="uint8")
    upper_hue = np.array([179, 255, 255], dtype="uint8")
    mask = cv2.inRange(hsv, lower_hue, upper_hue)
    return mask
def warpImg (img,points,w,h,inv=False):
    pts1 = np.float32(points)
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
    if inv:
    matrix = cv2.getPerspectiveTransform(pts2,pts1)
    else:
    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    imgwarp = cv2.warpPerspective(img,matrix,(w,h))

    return imgwarp

def nothing(a):
    pass
def initializeTrackbars(intialTracbarVals,wT=480, hT=240):
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 480, 240)
    cv2.createTrackbar("Width Top", "Trackbars", intialTracbarVals[0],wT//2, nothing)
    cv2.createTrackbar("Height Top", "Trackbars", intialTracbarVals[1], hT, nothing)
    cv2.createTrackbar("Width Bottom", "Trackbars", intialTracbarVals[2],wT//2, nothing)
    cv2.createTrackbar("Height Bottom", "Trackbars", intialTracbarVals[3], hT, nothing)
def valTrackbars(wT=480, hT=240):
    widthTop = cv2.getTrackbarPos("Width Top", "Trackbars")
    heightTop = cv2.getTrackbarPos("Height Top", "Trackbars")
    widthBottom = cv2.getTrackbarPos("Width Bottom", "Trackbars")
    heightBottom = cv2.getTrackbarPos("Height Bottom", "Trackbars")
    points = np.float32([(widthTop, heightTop), (wT-widthTop, heightTop),
    (widthBottom , heightBottom ), (wT-widthBottom, heightBottom)])
    return points
def drawPoints(img, points):
    for x in range(0, 4):
        cv2.circle(img, (int(points[x][0]), int(points[x][1])), 15, (0, 0, 255), cv2.FILLED)
    return img
def getHistogram(img, minPer=0.1, display=True, region=1):
    if region == 1:
        histValues = np.sum(img, axis=0)
    else:
        histValues = np.sum(img[img.shape[0] // region:, :], axis=0)
        #print(histValues)
        maxValue = np.max(histValues)
        minValue = minPer * maxValue
        indexArray = np.where(histValues >= minValue)
        basePoint = int(np.average(indexArray))
        #print(basePoint)
        # print(basePoint)
    if display:
        imgHist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    for x, intensity in enumerate(histValues):
        cv2.line(imgHist, (x, img.shape[0]), (x, img.shape[0] - int(intensity // 255 // region) ),
        (255, 0, 0), 1)
        cv2.circle(imgHist, (basePoint, img.shape[0]), 20, (0, 255, 255), cv2.FILLED)
        return basePoint, imgHist
        return basePoint


def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]

    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1],
                    imgArray[0][0].shape[0]), None, scale, scale)
    if len(imgArray[x][y].shape) == 2:
        imgArray[x][y]= cv2.cvtColor( imgArray[x][y],
        cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x]=cv2.resize(imgArray[x],(imgArray[0].shape[1],imgArray[0].shape[0]),None,scale, scale)
    if len(imgArray[x].shape)==2:imgArray[x]=cv2.cvtColor(imgArray[x],
        cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver


def detect_edges(frame):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 0 ], dtype="uint8")
    upper_white = np.array([0, 0, 0], dtype="uint8")
    mask = cv2.inRange(hsv, lower_white, upper_white)
    #cv2.imshow("masked", mask)
    #cv2.waitKey(0)
    # detect edges
    edges = cv2.Canny(mask, 50, 100)
    #cv2.imshow("edges",edges)
    #cv2.waitKey(0)
    return edges
def region_of_interest(edges):
    height, width = edges.shape #will be in format (height,width) or (rows,columns) , both are
    same as rows represent height :)
    mask = np.zeros_like(edges) #make a black picture of same shape as edges
    #cv2.imshow("masked", mask)
    #cv2.waitKey(0)
    # only focus lower half of the screen
    polygon = np.array([[(0, height),
    (0, height*0.375),
    (width, height*0.375),
    (width, height),
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255) #draw white color on mask in defined polygon
    #cv2.imshow('s', mask)
    #cv2.waitKey(0)
    cropped_edges = cv2.bitwise_and(edges, mask) #and respective pixels of edges and mask
    #cv2.imshow('cropped',cropped_edges)
    #cv2.waitKey(0)
    return cropped_edges