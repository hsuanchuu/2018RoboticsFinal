import numpy as np
import math


class Operation:
    def __init__(self):
        pass

    def rotation_matrix(self, theta):
        matrix = np.array([[math.cos(theta), -math.sin(theta), 0],
                           [math.sin(theta), math.cos(theta), 0],
                           [0, 0, 1]])
        return matrix
    def normalize_angle(self, angle):
        while angle > math.pi or angle <= -math.pi:
            if (angle > math.pi):
                angle = angle - 2 * math.pi
            if (angle <= -math.pi):
                angle = angle + 2 * math.pi
        return angle

    def local_to_global(self, local_x, local_y, local_theta,
                        robot_x, robot_y, robot_theta):
        temp = np.dot(self.rotation_matrix(robot_theta),
                      np.array([[local_x], [local_y], [local_theta]]))
        x = temp[0][0] + robot_x
        y = temp[1][0] + robot_y
        theta = temp[2][0] + robot_theta
        return [x, y, self.normalize_angle(theta)]

    def global_to_local(self, global_x, global_y, global_theta,
                        robot_x, robot_y, robot_theta):
        x = global_x - robot_x
        y = global_y - robot_y
        theta = global_theta - robot_theta
        result = np.dot(self.rotation_matrix(-robot_theta),
                        np.array([[x], [y], [theta]]))
        return [result[0][0], result[1][0], self.normalize_angle(result[2][0])]


