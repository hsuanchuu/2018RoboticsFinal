import time
import sys
import vision_definitions
import argparse
import qi
from naoqi import ALProxy

class FaceDetection(object):
    def __init__(self, session, args):
        super(FaceDetection, self).__init__()

        self.session = session
        self.args = args
        self.got_face = False

    #for connection
    def on_human_tracked(self, value):
        if value == []:
            self.got_face = False
        elif not self.got_face:
            self.got_face = True

            #Second field = array of face info
            faceInfoArray = value[1]
            for j in range(len(faceInfoArray)-1):
                faceInfo = faceInfoArray[j]

                #First field = Shape info
                faceShapeInfo = faceInfo[0]
                #Second field = Extra info (empty for now)
                faceExtraInfo = faceInfo[1]

                #Face tracking
                if j == 0:
                   self.tracker_proxy.registerTarget('Face',faceShapeInfo[3])
                   self.tracker_proxy.track('Face')

    def StartTracking(self):
        print('Starting FaceDetection')

        self.memory = self.session.service('ALMemory')
        self.face_detection = self.session.service('ALFaceDetection')
        self.tracker_proxy = ALProxy('ALTracker', self.args.ip, self.args.port)

        #Connect the event callback.
        self.subscriber = self.memory.subscriber('FaceDetected')
        self.subscriber.signal.connect(self.on_human_tracked)
        self.face_detection.subscribe('FaceDetection')

        self.got_face = False

        time.sleep(1.0)

    def StopTracking(self):
        #Stop face tracking
        self.tracker_proxy.stopTracker()
        self.tracker_proxy.unregisterAllTargets()
        print('ALTracker stopped')
        self.face_detection.unsubscribe('FaceDetection')

    def HumanDirection(self):
        motion_proxy = ALProxy('ALMotion', self.args.ip, self.args.port)
        humanDir = motion_proxy.getAngles('HeadYaw', \
                    True)
        print('Human direction: ' + str(humanDir[0]))
        return humanDir[0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1', 
            help='Robot IP address')
    parser.add_argument('--port', type=int, default=9559, 
            help='Naoqi port number')

    args = parser.parse_args()
    session = qi.Session()
    session.connect('tcp://' + args.ip + ':' + str(args.port))

    face_detection = FaceDetection(session,args)
    face_detection.GetFace()
