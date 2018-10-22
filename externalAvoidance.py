import time
import sys
import getopt
import argparse
import qi
def main(session):
    motion_service = session.service("ALMotion")
    motion_service.setExternalCollisionProtectionEnabled("All", True)
    motion_service.setMoveArmsEnabled(True,True)
	#motion_service.moveTo(0,0,-1.57)
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