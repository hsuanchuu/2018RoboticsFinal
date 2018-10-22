import argparse
import functools
import sys
import time
import math
from naoqi import ALProxy

class Motion(object):
    def __init__(self, session, args):
        self.motion_proxy = ALProxy('ALMotion', args.ip, args.port)
        self.posture_proxy = ALProxy('ALRobotPosture', args.ip, args.port)
        self.motion_service = session.service('ALMotion')
        """
        self.memory = session.service('ALMemory')
        self.motion_service = session.service('ALMotion')
        self.touch = self.memory.subscriber('TouchChanged')
        self.id = self.touch.signal.connect(functools.partial(\
                self.onTouched, 'TouchChanged'))
        """
    def external_avoidance(self):
        self.motion_service.setExternalCollisionProtectionEnabled("All", False)
    
    def init(self):
        self.posture_proxy.goToPosture('StandInit', 1.5)

    def raiseHead(self):
        self.motion_proxy.angleInterpolation('HeadPitch', -10* math.pi / 180.0, 1.0, True)
        
    def moveBack(self):
        self.motion_proxy.moveTo(0,0.6,0)   
    
    def take_object(self):
        self.rArmTouched = False
        #Set collision protection disabled
        self.motion_proxy.setExternalCollisionProtectionEnabled('All', False)
        self.posture_proxy.goToPosture('StandInit', 1.5)
        #turn 90 degrees
        self.motion_proxy.moveTo(0,0,1.57)

        #Prepare to take
        self.jointList = ['HipPitch', 'RShoulderRoll', 'RElbowRoll', 'RElbowYaw', 'RHand']
        self.angleList = [(-29.0* math.pi / 180.0), (-30* math.pi / 180.0), (59.3* math.pi / 180.0), (93.4* math.pi / 180.0), 0.98]
        self.timeList = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.motion_proxy.angleInterpolation(self.jointList, self.angleList, self.timeList, True)
        #take
        self.jointList = ['RShoulderPitch', 'RWristYaw', 'RShoulderRoll', 'RHand']
        self.angleList = [(44.2* math.pi / 180.0), (-0.4* math.pi / 180.0), (-3.3* math.pi / 180.0), 0.28]
        self.timeList = [1.0, 2.0, 3.0, 4.0]
        self.motion_proxy.angleInterpolation(self.jointList, self.angleList, self.timeList, True)
        time.sleep(2.0)
        #lift
        self.jointList = ['RElbowRoll']
        self.angleList = [(78.4* math.pi / 180.0)]
        self.motion_proxy.angleInterpolation(self.jointList, self.angleList, 1.0, True)
        self.motion_service.setMoveArmsEnabled(False,False)
        self.motion_proxy.moveTo(0,0,-1.57)
        
        time.sleep(1.0) #Shake hand in 5 seconds

        '''while(self.rArmTouched == False):
            time.sleep(0.5)'''
        self.motion_proxy.angleInterpolation('RHand', 0.98,1.0, True)
        self.posture_proxy.goToPosture('StandInit', 1.5)
       
    def turn(self, turn_angle):
        self.motion_proxy.moveTo(0,0,turn_angle)
    def raiseHand(self, direction):
        if(direction == 0):#right
            self.jointList = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw' ]
            self.angleList = [(56.1 * math.pi / 180.0), (42.2 * math.pi / 180.0), (-72.4 * math.pi / 180.0), (-20.7 * math.pi / 180.0), (-81.8 * math.pi / 180.0)]
            self.timeList = [0.5, 1.0, 1.5, 2.0, 2.5]
        else:#left
            self.jointList = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw' ]
            self.angleList = [(56.1 * math.pi / 180.0), (-42.2 * math.pi / 180.0), (72.4 * math.pi / 180.0), (20.7 * math.pi / 180.0), (81.8 * math.pi / 180.0)]
            self.timeList = [0.5, 1.0, 1.5, 2.0, 2.5]
        self.motion_proxy.angleInterpolation(self.jointList, self.angleList, self.timeList, True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1', 
            help='Robot IP address')
    parser.add_argument('--port', type=int, default=9559, 
            help='Naoqi port number')

    import qi
    args = parser.parse_args()
    session = qi.Session()
    session.connect('tcp://' + args.ip + ':' + str(args.port))

    motion = Motion(session,args)
    motion.take_object()
