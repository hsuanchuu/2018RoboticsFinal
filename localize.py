#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use localization methods"""

import qi
import argparse
import sys


class Navigate(object):
    def __init__(self, session, args):
        super(Navigate, self).__init__()

        self.session = session
        self.args = args
        self.navigation_service = session.service("ALNavigation")
        self.navigation_service.stopLocalization()
        self.motion_service = session.service("ALMotion")
        self.currentPos=[0.0,0.0,0.0]
        #restroom, egg, fruits,vegetables, meat,cashier
        self.pos=[[3.6,-0.6,0],[-6,-2,0],[-6,2,0],[4,0,0],[4.0,-1.0,0],[2.4,-0.6,0]] #all positions
        self.navigation_service.loadExploration("/home/nao/.local/share/Explorer/2018-01-05T081342.632Z.explo")

    def getPosition(self):
        self.navigation_service.startLocalization()
        print(self.navigation_service.getRobotPositionInMap()[0])
    
    def goto(self,posIndex):
        self.navigation_service.relocalizeInMap(self.currentPos)
        self.navigation_service.startLocalization()
        print "I am at: "+str(self.navigation_service.getRobotPositionInMap()[0])
        # Navigate to another place in the map
        self.navigation_service.navigateToInMap(self.pos[posIndex])
        print "I want to go to: "+str(self.pos[posIndex])
        # Check where the robot arrived
        print "I reached: " + str(self.navigation_service.getRobotPositionInMap()[0])
        #self.currentPos=self.navigation_service.getRobotPositionInMap()[0]
        self.currentPos=self.pos[posIndex]
    def reset(self,direction):
        self.currentPos[2]+=direction
        print "currentPos: "+str(self.currentPos)
        self.navigation_service.relocalizeInMap(self.currentPos)
        self.navigation_service.startLocalization()
        print "I am at: "+str(self.navigation_service.getRobotPositionInMap()[0])
        # Navigate to another place in the map
        self.navigation_service.navigateToInMap([0,0,0])
        # Check where the robot arrived
        print "I reached: " + str(self.navigation_service.getRobotPositionInMap()[0])
        #self.currentPos=self.navigation_service.getRobotPositionInMap()[0]
        self.currentPos=[0,0,0]
    def stop(self):
        # Stop localization
        self.navigation_service.stopLocalization()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--explo", type=str, help="Path to .explo file.")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    navigate=Navigate(session,args)
    #print(navigate.getPosition())
    navigate.goto(5)
    #navigate.reset()
    navigate.stop()
