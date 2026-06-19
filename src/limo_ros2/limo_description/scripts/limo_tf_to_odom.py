#!/usr/bin/env python3
import math

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from tf2_msgs.msg import TFMessage


class LimoTfToOdom(Node):
    def __init__(self):
        super().__init__('limo_tf_to_odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('input_tf_topic', 'tf')
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.input_tf_topic = self.get_parameter('input_tf_topic').value
        self.previous = None

        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.tf_sub = self.create_subscription(TFMessage, self.input_tf_topic, self.on_tf, 50)

    def on_tf(self, msg):
        for transform in msg.transforms:
            if transform.header.frame_id != self.odom_frame:
                continue
            if transform.child_frame_id != self.base_frame:
                continue
            self.publish_odom(transform)

    def publish_odom(self, transform):
        odom = Odometry()
        odom.header = transform.header
        odom.child_frame_id = transform.child_frame_id
        odom.pose.pose.position.x = transform.transform.translation.x
        odom.pose.pose.position.y = transform.transform.translation.y
        odom.pose.pose.position.z = transform.transform.translation.z
        odom.pose.pose.orientation = transform.transform.rotation

        stamp = transform.header.stamp.sec + transform.header.stamp.nanosec * 1e-9
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y
        yaw = self.yaw_from_quaternion(odom.pose.pose.orientation)

        if self.previous is not None:
            last_stamp, last_x, last_y, last_yaw = self.previous
            if stamp <= last_stamp:
                return
            dt = stamp - last_stamp
            if dt > 1e-6:
                odom.twist.twist.linear.x = math.hypot(x - last_x, y - last_y) / dt
                odom.twist.twist.angular.z = self.normalize_angle(yaw - last_yaw) / dt

        self.previous = (stamp, x, y, yaw)
        self.odom_pub.publish(odom)
        self.publish_tf(transform)

    def publish_tf(self, transform):
        filtered_transform = TransformStamped()
        filtered_transform.header = transform.header
        filtered_transform.child_frame_id = transform.child_frame_id
        filtered_transform.transform = transform.transform
        self.tf_broadcaster.sendTransform(filtered_transform)

    @staticmethod
    def yaw_from_quaternion(q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    @staticmethod
    def normalize_angle(angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle


def main():
    rclpy.init()
    node = LimoTfToOdom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
