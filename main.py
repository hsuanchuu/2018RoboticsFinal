import qi
import time
import sys
import getopt
import argparse

from FaceDetection import FaceDetection
from Motion import Motion
from ShowImage import ShowImage
from localize import Navigate
import Landmark as landmark

def findHuman(hand):
    faceDetection.StartTracking()
    motion.raiseHead()
    count=0
    while not faceDetection.got_face:
        motion.turn(-1.57)
        count-=1.57
        time.sleep(2.0)
    motion.turn(faceDetection.HumanDirection())
    motion.raiseHand(hand)
    time.sleep(2.0)
    faceDetection.StopTracking()
    motion.init()
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1', 
            help='Robot IP address')
    parser.add_argument('--port', type=int, default=9559, 
            help='Naoqi port number')

    args = parser.parse_args()
    session = qi.Session()
    session.connect('tcp://' + args.ip + ':' + str(args.port))

    faceDetection = FaceDetection(session,args)
    #faceDetection.StopTracking()
    #model1 = Model1()
    #model2 = Model2()
    showImage = ShowImage(session,args)
    navigate = Navigate(session,args)
    motion=Motion(session,args)
    motion.external_avoidance()
    right=0
    left=1
    count=0
    while count==0:
        #the argument predicted by the pose
        #command=model1.predict()
        count+=1
        motion.init()
        command=0
        faceDetection.StartTracking()
        while not faceDetection.got_face:
            time.sleep(1.0)
        showImage.show(command)
        faceDetection.StopTracking()
        if command==7:
            continue
        #yesOrNo=model2.predict()
        yesOrNo=0
        if yesOrNo==0:
            if command==0:
                showImage.show(command+8)
                navigate.goto(command)
                direction=findHuman(right)
                navigate.reset(direction)
                navigate.stop()
                landmark.main(session)
                motion.moveBack()
            elif command==1:
                showImage.show(command+8)
                motion.getObject()
            elif 2<=command<=5:
                showImage.show(10)
                navigate.goto(command-1)
                direction=findHuman(left)
                navigate.reset(direction)
                navigate.stop()
                landmark.main(session)
                motion.moveBack()
            else:
                showImage.show(11)
                navigate.goto(command-1)
                direction=findHuman(right)
                navigate.reset(direction)
                navigate.stop()
                landmark.main(session)
                motion.moveBack()
        else:
            showImage.show(12)
 
