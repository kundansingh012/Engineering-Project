#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration
from sensor_msgs.msg import LaserScan
from std_srvs.srv import Trigger
import math, time, threading


class SmartCommander(Node):
    def __init__(self):
        # Initialize the ROS2 node with name 'smart_commander_node
        super().__init__('smart_commander_node')

        # Initialize Nav2 navigation system
        # This provides path planning and navigation capabilities
        self.navigator = BasicNavigator()

        # Set up LiDAR subscription to detect gate status
        # Subscribes to the /scan topic with queue size of 10
        self.lidar_subscriber = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)
        self.gate_is_open = False

        # Create service clients for pick and place operations
        # These will be used to trigger the robot's pick and place actions
        self.pick_client = self.create_client(Trigger, '/automatic_pick/pick')
        self.place_client = self.create_client(Trigger, '/automatic_pick/place')

        # Define all waypoints for the mission
        # Each point is [x, y, yaw_angle] in map coordinates
        self.start_point = [0.2865008230829143, -0.38103989467820204, -91.3611781]  # Start point
        self.pos1 = [0.443909826049881, -1.0461364782520837, -114.8028034] # just looking
        #self.pos2 =[0.2760221430853639, -1.4011322004196591, -134.6882527] # just looking
        self.pos3 = [0.2957670699597659, -1.3548445184352513, -110.1381423]# Pick-up location
        self.pos4 = [0.26142510279893905, -1.324094106117701, -49.835294]  # Mid waypoint before gate
        self.before_gate = [1.3296841054680366, -1.4028787892834917, 87.3336303]  # Stop before gate
        self.drop = [1.5125243103723636, -0.42820928507381195, 42.7508417]  # drop location (after passing gate)
        self.return_gate = [1.4092829843659862, -0.6680072016477144, -87.6255339]  # Wait before returning


        # Start the mission in a separate thread to prevent blocking
        self.mission_thread = threading.Thread(target=self.run_mission)
        self.mission_thread.start()

    # ----------------------------------------------------------
    # LIDAR callback to check if gate area is clear/open
    # ----------------------------------------------------------
    def lidar_callback(self, msg):
        front_index = len(msg.ranges) // 2
        distance = msg.ranges[front_index]
        # Gate is considered open if distance is infinite or greater than 0.2 meters
        if math.isinf(distance) or distance > 0.2:
            self.gate_is_open = True
        else:
            self.gate_is_open = False

    # ----------------------------------------------------------
    # Wait until gate is open (based on LiDAR distance)
    # ----------------------------------------------------------
    def wait_for_gate(self, label="gate"):
        self.get_logger().info(f"Waiting for {label} to open...")
        while rclpy.ok() and not self.gate_is_open:
            rclpy.spin_once(self, timeout_sec=0.1)
            self.get_logger().info(f"{label.capitalize()} closed. Waiting...", throttle_duration_sec=3)
            time.sleep(1)
        self.get_logger().info(f"{label.capitalize()} is open! Proceeding...")

    # ----------------------------------------------------------
    # Trigger pick/place actions through automatic_pick services
    # ----------------------------------------------------------
    def call_service(self, client, name, wait_time=15):
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(f"{name} service not available!")
            return False
        # Create and send service request
        req = Trigger.Request()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() and future.result().success:
            self.get_logger().info(f"{name} action triggered successfully.")
            # Wait for the physical motion to finish
            self.get_logger().info(f"Waiting {wait_time}s for {name} to complete...")
            time.sleep(wait_time)
            self.get_logger().info(f"{name} action completed successfully.")
            return True
        else:
            self.get_logger().error(f"{name} action failed.")
            return False

    # ----------------------------------------------------------
    # Main mission execution loop
    # Handles the complete pick and place cycle including navigation
    # ----------------------------------------------------------
    def run_mission(self):
        # Wait until Nav2 is ready
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Nav2 active. Starting full mission.")

        cycle_count = 0
        while rclpy.ok():  # Run continuously until shutdown
            try:
                cycle_count += 1
                self.get_logger().info(f"\nStarting mission cycle {cycle_count}")

                # Execute pick-and-place sequence
                # 1. Navigate to pick location and perform pick
                self.get_logger().info("Navigating to PICK location...")
                self.navigate_to_goal(*self.pos3)
                self.call_service(self.pick_client, "Pick", wait_time=30)

                # 2. Navigate through intermediate points
                self.navigate_to_goal(*self.pos4)

                # 3 Navigate through intermediate points before gate
                self.get_logger().info("Navigating to BEFORE-GATE point...")
                self.navigate_to_goal(*self.before_gate)
                self.wait_for_gate("Entry Gate")

                # 4 Navigate to drop location and perform place
                self.get_logger().info("Navigating through gate to PLACE location...")
                self.navigate_to_goal(*self.drop)
                self.call_service(self.place_client, "Place", wait_time=15)

                # 5 Return journey (after gate)
                self.get_logger().info("Navigating to AFTER-GATE waiting point...")
                self.navigate_to_goal(*self.return_gate)
                self.wait_for_gate("Exit Gate")

                # 9 Return journey (home)
                self.get_logger().info("Returning to HOME location...")
                self.navigate_to_goal(*self.start_point)

                self.get_logger().info(f"Mission Cycle {cycle_count} Completed Successfully")

            except Exception as e:
                self.get_logger().error(f"Mission cycle {cycle_count} failed: {str(e)}")
                # Optional: Add a short delay before retrying
                time.sleep(2) # Wait before retrying
                continue

    # ----------------------------------------------------------
    # Navigation function (send goal to Nav2)
    # ----------------------------------------------------------
    def navigate_to_goal(self, x, y, yaw_degrees):
        # Create goal pose message
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        # Set position
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        # Convert yaw from degrees to quaternion
        yaw = math.radians(yaw_degrees)
        goal_pose.pose.orientation.z = math.sin(yaw / 2)
        goal_pose.pose.orientation.w = math.cos(yaw / 2)

        # Send goal and monitor progress
        self.navigator.goToPose(goal_pose)

        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            if feedback:
                eta = Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9
                self.get_logger().info(f"ETA: {eta:.0f}s", throttle_duration_sec=5)
            rclpy.spin_once(self, timeout_sec=0.1)

        # Check result
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Goal reached successfully.")
            return True
        else:
            self.get_logger().error("Navigation failed.")
            return False


def main(args=None):
    rclpy.init(args=args)
    commander = SmartCommander()
    commander.mission_thread.join()
    commander.destroy_node()


if __name__ == "__main__":
    main()
