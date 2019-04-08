#!/usr/bin/env python

from imutils import face_utils
from moviepy.editor import *
import numpy as np
import cv2
import sys
import os
import argparse
import imutils
import dlib

numPoints = 0
clickedPoints = []
UPLOAD_FOLDER = os.path.basename('uploads')
MORPH_FOLDER = os.path.basename('facemorph')
CARTOON_FOLDER = os.path.join(MORPH_FOLDER, os.path.basename("cartoons"))

# Read points from text file
def readPoints(path) :
    # Create an array of points.
    points = []
    # Read points
    with open(path) as file :
        for line in file :
            x, y = line.split()
            points.append((int(x), int(y)))

    return points

# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def applyAffineTransform(src, srcTri, dstTri, size) :
    
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform( np.float32(srcTri), np.float32(dstTri) )
    
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine( src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst


# Warps and alpha blends triangular regions from img1 and img2 to img
def morphTriangle(img1, img2, img, t1, t2, t, alpha) :

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))
    r = cv2.boundingRect(np.float32([t]))


    # Offset points by left top corner of the respective rectangles
    t1Rect = []
    t2Rect = []
    tRect = []


    for i in range(0, 3):
        tRect.append(((t[i][0] - r[0]),(t[i][1] - r[1])))
        t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))


    # Get mask by filling triangle
    mask = np.zeros((r[3], r[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(tRect), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    img2Rect = img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]]

    size = (r[2], r[3])
    warpImage1 = applyAffineTransform(img1Rect, t1Rect, tRect, size)
    warpImage2 = applyAffineTransform(img2Rect, t2Rect, tRect, size)

    # Alpha blend rectangular patches
    imgRect = (1.0 - alpha) * warpImage1 + alpha * warpImage2

    # Copy triangular region of the rectangular patch to the output image
    img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] = img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] * ( 1 - mask ) + imgRect * mask

def facialLandmarks(image, fileName):
    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    # load the input image, resize it, and convert it to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    picDimensions = image.shape
    picHeight = image.shape[0]
    picWidth = image.shape[1]

    # detect faces in the grayscale image
    rects = detector(gray, 1)

    # loop over the face detections
    for (i, rect) in enumerate(rects):
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # add left ear, neck, right shoulder (their right, our left), and left shoulder
        leftEar = clickedPoints[0]
        neck = clickedPoints[1]
        rightShoulder = clickedPoints[2]
        leftShoulder = clickedPoints[3]
        newPoints = np.array([leftEar,
                            neck,
                            rightShoulder,
                            leftShoulder,
                            [0, 0], 
                            [0, (picHeight/2 - 1)], 
                            [0, picHeight - 1], 
                            [(picWidth/2 - 1), picHeight - 1], 
                            [picWidth - 1, picHeight - 1], 
                            [picWidth - 1, (picHeight/2 - 1)], 
                            [picWidth - 1, 0], 
                            [(picWidth/2 - 1), 0]])
        shape = np.concatenate((shape, newPoints))
        file = open('face.txt', "w")
        file.write(str(shape))
        file.close()

# opens face.txt, removes "[", "]", "." and saves it to output file
def parse(fileName):
    f = open("face.txt")
    simple = f.read()
    openBrace = simple.replace("[", "")
    closedBrace = openBrace.replace("]", "")
    period = closedBrace.replace(".", "")
    close= open(fileName + '.txt', "w")
    # needed to get one space before start of text to align numbers
    close.write(" ")
    close.write(period)

def click_event(event, x, y, flags, param):
    global numPoints
    global clickedPoints
    if event == cv2.EVENT_LBUTTONDOWN and numPoints != 4:
        newPoint = x, y
        clickedPoints.append(newPoint)
        numPoints += 1

def morph(personPic, cartoonPic = "anna.jpg"):
    # Read images
    personPath = os.path.join(UPLOAD_FOLDER, personPic)
    cartoonPath = os.path.join(CARTOON_FOLDER, cartoonPic)
    img1 = cv2.imread(personPath)
    img2 = cv2.imread(cartoonPath)

    img1 = cv2.resize(img1, (600, 800))
    cv2.imwrite(personPath, img1)
    
    cv2.imshow("Original Face", img1)
    cv2.setMouseCallback("Original Face", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Find facial landmarks of selfie and create text file of landmark points
    facialLandmarks(img1, personPath)
    parse(personPath)
    
    # Convert Mat to float data type
    img1 = np.float32(img1)
    img2 = np.float32(img2)

    img_array = []

    for i in range(0, 100):
        alpha = i/100

        # Read array of corresponding points
        points1 = readPoints(personPath + '.txt')
        points2 = readPoints(cartoonPath + '.txt')
        print(len(points2), len(points1))
        points = []

        # Compute weighted average point coordinates
        for j in range(0, len(points2)):
            x = ( 1 - alpha ) * points1[j][0] + alpha * points2[j][0]
            y = ( 1 - alpha ) * points1[j][1] + alpha * points2[j][1]
            points.append((x,y))


        # Allocate space for final output
        imgMorph = np.zeros(img1.shape, dtype = img1.dtype)

        # Read triangles from tri.txt
        with open("tri_orig.txt") as file :
            for line in file :
                x,y,z = line.split()
                
                x = int(x)
                y = int(y)
                z = int(z)

                t1 = [points1[x], points1[y], points1[z]]
                t2 = [points2[x], points2[y], points2[z]]
                t = [ points[x], points[y], points[z] ]

                # Morph one triangle at a time.
                morphTriangle(img1, img2, imgMorph, t1, t2, t, alpha)

        # Display Result
        finalImage = np.uint8(imgMorph)
        img_array.append(finalImage)

    # Create file names for morph video and gif
    video_name = os.path.join(MORPH_FOLDER, personPic.split(".")[0] + "morph.mp4")
    gif_name = os.path.join(MORPH_FOLDER, personPic.split(".")[0] + "morph.gif")
    
    # Creates mp4 of morphing from person to cartoon
    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 50, (600, 800))

    for i in range(len(img_array)):
        out.write(img_array[i])
        if i == 50:
            cv2.imshow("Morphed Image", img_array[i])
            cv2.waitKey(0)
    out.release()

    # Creates gif of morphing from mp4
    clip = (VideoFileClip(video_name))
    clip.write_gif(gif_name)

    return gif_name