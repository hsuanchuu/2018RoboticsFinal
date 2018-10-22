#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Demonstrates how to use the ALVisionRecognition module."""

import qi
import time
import sys
import argparse


class VisionRecognition(object):
    """
    We first instantiate a proxy to the ALVisionRecognition module
    You need to record an Object on choregraphe then show it to
    the robot during the script run.
    Note that this module should be loaded on the robot's naoqi.
    The module output its results in ALMemory in a variable
    called "PictureDetected".
    We then read this ALMemory value and check whether we get
    interesting things.
    """

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        super(VisionRecognition, self).__init__()
        app.start()
        session = app.session
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Connect the event callback.
        self.subscriber = self.memory.subscriber("PictureDetected")
        self.subscriber.signal.connect(self.on_picture_detected)
        # Get the services ALTextToSpeech and ALVisionRecognition.
        self.tts = session.service("ALTextToSpeech")
        self.vision_recognition = session.service("ALVisionRecognition")
        self.vision_recognition.subscribe("VisionRecognition", 500, 0.0 )
        self.got_picture = False

    def on_picture_detected(self, value):
        """
        Callback for event PictureDetected.
        """
        if value == []:  # empty value when the recognized object disappears
            self.got_picture = False
        elif not self.got_picture:  # only speak the first time a recognized object appears
            self.got_picture = True
            print "I saw a recognized object! "
            self.tts.say("I saw a recognized object! ")
            # First Field = TimeStamp.
            timeStamp = value[0]
            print "TimeStamp is: " + str(timeStamp)
            object_data = value[1]
            print "Object data: " + str(object_data)



    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting VisionRecognition"
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping VisionRecognition"
            self.vision_recognition.unsubscribe("VisionRecognition")
            #stop
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["VisionRecognition", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    picture_detector = VisionRecognition(app)
    picture_detector.run()
