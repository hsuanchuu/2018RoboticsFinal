import math
import numpy as np
import operation
import almath
import time
import sys
import getopt
import argparse
import qi

move_config = [["MaxVelXY", 0.22], ["MaxVelTheta", 0.5]]
linear_error = 0.15
angular_error = 0.1

def velocity_adjustment(relative_pose):
    relative_distance = math.sqrt(pow(relative_pose[0], 2) +
                                  pow(relative_pose[1], 2))
    if relative_distance >= 5:
        maximum_linear_velocity = 0.3
    elif 3 <= relative_distance < 5:
        maximum_linear_velocity = 0.25
    else:
        maximum_linear_velocity = 0.2

    if math.fabs(relative_pose[2]) >= 1.57:
        maximum_angular_velocity = 0.3
    else:
        maximum_angular_velocity = 0.2

    config = [["MaxVelXY", maximum_linear_velocity],
              ["MaxVelTheta", maximum_angular_velocity]]
    return config

class landmark_detection:
    
    def __init__(self, session):
        print "landmark"
        self.operation = operation.Operation()
        #LandmarkPose() is a fn. defined below
	self.landmark_pose = LandmarkPose()
        self.memory_service = session.service("ALMemory")
        self.motion_service = session.service("ALMotion")
        self.posture_service = session.service("ALRobotPosture")
        self.manager_service = session.service("ALBehaviorManager")
        self.behaviorName = "landmardetection-b5c7a4/behavior_1"
        self.sub()
        
    def sub(self):      
        if (not self.manager_service.isBehaviorRunning(self.behaviorName)):
            self.manager_service.runBehavior(self.behaviorName)
            time.sleep(0.5)
        else:
            print "Behavior is already running."
            
        self.landmark_sub = self.memory_service.subscriber("landmarkInformation")   
        self.landmark_signal = self.landmark_sub.signal.connect(self.is_detected)
        
        
    def stop(self):
        try:
            self.landmark_sub.signal.disconnect(self.landmark_signal)
        except:
            pass
    
    def is_detected(self, value):
        if 1<=value[6]<=6:
            print "detection"
            print "Landmark " + str(value[6]) + " is detected!"
            self.memory_service.insertData("priority",5)
            # Calculate the relative pose to the robot frame
            current_global_goal = self.memory_service.getData("goal")
            #print "current_global_goal: ",current_global_goal
            landmark_global_pose = self.landmark_pose.get_pose(value[6])
            #print  "landmark_global_pose: ",landmark_global_pose
            currVel = self.motion_service.getRobotVelocity()
          
            #print "currVel",currVel
            #print  "current_global_goal",current_global_goal
            current_global_goal_2 = [a - b*1.2 for a,b in zip(current_global_goal, currVel )]
            current_global_goal = current_global_goal_2
            name = 'CameraBottom'
            frame = 2
            use_sensor_values = True
            camera_pose = self.motion_service.getPosition(name, frame, use_sensor_values)
            temp = math.sqrt(math.pow(value[1] * 0.001, 2) +
                           math.pow(value[2] * 0.001, 2))
            x_offset = math.sqrt(math.pow(temp, 2) - math.pow(camera_pose[2], 2)) + camera_pose[0]
            y_offset = - value[0] * 0.001
            theta_offset = -value[5]
          
            rotation_matrix = self.operation.rotation_matrix((landmark_global_pose[2] - theta_offset))
            transform = np.dot(rotation_matrix,
                             np.array([[x_offset], [y_offset], [theta_offset]]))
            current_robot_pose = [landmark_global_pose[0] - transform[0][0],
                                landmark_global_pose[1] - transform[1][0],
                                self.operation.normalize_angle(landmark_global_pose[2] - transform[2][0])]
            results = self.operation.global_to_local(current_global_goal[0],
                                                   current_global_goal[1],
                                                   current_global_goal[2],
                                                   current_robot_pose[0],
                                                   current_robot_pose[1],
                                                   current_robot_pose[2])

            # Adjust movement
            adjust_config = velocity_adjustment(results)
            init_pose = almath.Pose2D(self.motion_service.getRobotPosition(True))
            target_distance = almath.Pose2D(results[0], results[1], results[2])
            expected_end_pose = init_pose * target_distance
            self.motion_service.moveTo(float(results[0]), float(results[1]), float(results[2]), adjust_config)
            # Check if reach the goal
            real_end_pose = almath.Pose2D(self.motion_service.getRobotPosition(True))
            position_error = real_end_pose.diff(expected_end_pose)
            position_error.theta = almath.modulo2PI(position_error.theta)
            if abs(position_error.x) < linear_error \
                and abs(position_error.y) < linear_error \
                and abs(position_error.theta) < angular_error:
                print "Arrived"
                self.memory_service.insertData("state","finished")
            else:
                print "Not arrived"
                #self.memory_service.insertData("state","finished")

class LandmarkPose:
    def __init__(self):
        # Landmark Pose at YL
        #grid_size = 0.45
        self.pose = [[2.1,0.3,-1.57],
                 [1.5,0.3,3.14],
                 [0,0,0],
                 [0,0.0,0],
                 [0.9,0.3,1.57],
                 [0.9,-0.3,0]]
       
    def get_pose(self, index):
        return self.pose[index - 1]
 
        
   
def move_to_dest(session, current_robot_pose, goal):
    op = operation.Operation()
    pi = math.pi
    current_positon = current_robot_pose
    motion_service = session.service("ALMotion")
    memory_service = session.service("ALMemory")
    theta_difference = op.normalize_angle(goal[2]-current_robot_pose[2])
    #theta_difference = math.atan2(goal[1]-current_robot_pose[1],goal[0]-current_robot_pose[0])-current_robot_pose[2]
    LD.stop()
    memory_service.insertData("goal",goal)
    motion_service.moveTo(0.0,0.0,theta_difference,move_config)  
    current_robot_pose[2] = math.atan2(goal[1],goal[0])
    motion_service.angleInterpolation("HeadPitch", -0.10584473609924316, 0.5, True)
    memory_service.insertData("state","start")
    LD.sub()
    memory_service.insertData("dV3", [0.0,0.0,0.0,0.0])
    #exp_dist =math.hypot(goal[1]-current_robot_pose[1],goal[0]-current_robot_pose[0])
    init_position = motion_service.getRobotPosition(True)
    if goal[2]>3 or goal[2]<-3:
        print "a",current_robot_pose[0]-goal[0],current_robot_pose[1]-goal[1]
        motion_service.moveTo(current_robot_pose[0]-goal[0],current_robot_pose[1]-goal[1],0.0)
    else:
        print "b",goal[0]-current_robot_pose[0],goal[1]-current_robot_pose[1]
        motion_service.moveTo(goal[0]-current_robot_pose[0],goal[1]-current_robot_pose[1],0.0)
    
    while memory_service.getData("state")=="start":
        pass
    
def main(session):
    memory_service = session.service("ALMemory")
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")
    posture_service.goToPosture("StandInit",0.5)
    motion_service.setOrthogonalSecurityDistance(0.01)
    motion_service.setTangentialSecurityDistance(0.01)
    
    motion_service.setExternalCollisionProtectionEnabled("All", True)
    global LD
    LD = landmark_detection(session)
    ###
    #LD.stop()
    #motion_service.moveTo(0.0,0.0,-120*3.14/180.0)
    #motion_service.moveTo(1.2,0.0,0.0,12.0)
    #LD.sub()
    move_to_dest(session,[-1.0,0.0,0.0],[0.0,0.0,0.0])
    LD.stop()
    ###
    

if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.188",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    
    args = parser.parse_args()
    connection_url = "tcp://" + args.ip + ":" + str(args.port)
    session = qi.Session()
   
    try:
        session.connect(connection_url)
       
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    main(session)


