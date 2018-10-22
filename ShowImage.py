#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use showImage Method"""

import qi
import argparse
import sys
import time

class ShowImage(object):
    def __init__(self, session, args):
        super(ShowImage, self).__init__()

        self.session = session
        self.args = args
        self.tabletService = session.service("ALTabletService")
        self.picture=[ "restroom.png","product.png","eggs.png","fruits.png",\
                       "vegetables.png","meat.png","checkout.png","sorry.png",\
                       "restroomLead.png","giveCup.png","followMe.png",\
                       "cashierLead.png","what.png"]

    def show(self,pictureIndex):
        """
        This example uses the showImage method.
        To Test ALTabletService, you need to run the script ON the robot.
        """
        # Get the service ALTabletService.

        try:
            self.tabletService.enableWifi()
            # Display a local image located in img folder in the root of the web server
            # The ip of the robot from the tablet is 198.18.0.1
            self.tabletService.preLoadImage("http://198.18.0.1/apps/showimage-98094b/"+self.picture[pictureIndex])
            self.tabletService.showImage("http://198.18.0.1/apps/showimage-98094b/"+self.picture[pictureIndex])
            # print(str("http://"+str(self.tabletService.robotIp())+"/html/cashierLead.png"))
            time.sleep(5.0)

            # Hide the web view
            self.tabletService.hideImage()
        except Exception, e:
            print "Error was: ", e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    showImage = ShowImage(session,args)
    showImage.show(1)
