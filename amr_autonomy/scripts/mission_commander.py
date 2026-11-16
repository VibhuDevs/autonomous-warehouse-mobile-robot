#!/usr/bin/env python3

import math
import re
import threading
from pathlib import Path

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import String
from action_msgs.msg import GoalStatus


class MissionCommander(Node):
    def __init__(self):
        super().__init__('mission_commander')
        self.declare_parameter('use_sim_time', True)
        self.declare_parameter(
            'locations_file',
            str(
                Path(get_package_share_directory('amr_autonomy'))
                / 'config'
                / 'locations.yaml'
            ),
        )
        self._locations = self._load_locations(
            self.get_parameter('locations_file').value
        )
        self._callback_group = ReentrantCallbackGroup()
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose',
            callback_group=self._callback_group,
        )
        self._lock = threading.Lock()
        self._mission_active = False
        self._goal_handle = None
        self._wait_timer = None
        self._subscription = self.create_subscription(
            String,
            '/amr_autonomy/command',
            self._on_command,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
            ),
            callback_group=self._callback_group,
        )
        self.get_logger().info(
            'Ready for aisle commands on /amr_autonomy/command '
            '(examples: aisle1, "go to aisle 2").'
        )

    @staticmethod
    def _load_locations(locations_file):
        with open(locations_file, encoding='utf-8') as stream:
            locations = yaml.safe_load(stream)
        if not isinstance(locations, dict):
            raise ValueError(f'Locations file must contain a mapping: {locations_file}')

        for name in ('initial_pose', 'pickup_point'):
            if name not in locations:
                raise ValueError(f'Missing required location "{name}" in {locations_file}')

        for name, pose in locations.items():
            if (
                not isinstance(name, str)
                or not isinstance(pose, list)
                or len(pose) != 3
                or not all(isinstance(value, (int, float)) for value in pose)
                or not all(math.isfinite(value) for value in pose)
            ):
                raise ValueError(
                    f'Location "{name}" must be a finite [x, y, yaw] list.'
                )
        if not any(name.startswith('aisle') for name in locations):
            raise ValueError('Locations file must define at least one aisle target.')
        return locations

    def _on_command(self, message):
        destination = self._resolve_destination(message.data)
        if destination is None:
            aisles = ', '.join(
                name for name in self._locations if name.startswith('aisle')
            )
            self.get_logger().error(
                f'Unknown mission command "{message.data}". Available destinations: '
                f'{aisles}.'
            )
            return

        with self._lock:
            if self._mission_active:
                self.get_logger().warning(
                    'Ignoring command because a pickup-and-return mission is already active.'
                )
                return
            self._mission_active = True

        self._targets = [
            ('pickup_point', self._locations['pickup_point']),
            (destination, self._locations[destination]),
            ('initial_pose', self._locations['initial_pose']),
        ]
        self._target_index = 0
        self.get_logger().info(
            f'Starting mission: pickup_point -> {destination} -> initial_pose.'
        )
        self._send_current_goal()

    def _resolve_destination(self, command):
        normalized = re.sub(r'[^a-z0-9]', '', command.lower())
        match = re.search(r'aisle\s*([0-9]+)', command.lower())
        if match:
            destination = f'aisle{match.group(1)}'
            return destination if destination in self._locations else None
        for name in self._locations:
            if name.startswith('aisle') and normalized == re.sub(
                r'[^a-z0-9]', '', name.lower()
            ):
                return name
        return None

    def _send_current_goal(self):
        name, values = self._targets[self._target_index]
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(values[0])
        pose.pose.position.y = float(values[1])
        pose.pose.position.z = 0.0
        pose.pose.orientation.z = math.sin(float(values[2]) / 2.0)
        pose.pose.orientation.w = math.cos(float(values[2]) / 2.0)

        goal = NavigateToPose.Goal()
        goal.pose = pose
        self.get_logger().info(
            f'Navigating to {name}: x={values[0]:.2f}, y={values[1]:.2f}, '
            f'yaw={values[2]:.2f}.'
        )
        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal)
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future):
        try:
            self._goal_handle = future.result()
        except Exception as error:
            self._finish_mission(f'Failed to send navigation goal: {error}', failed=True)
            return
        if not self._goal_handle.accepted:
            self._finish_mission('Nav2 rejected the navigation goal.', failed=True)
            return
        self._goal_handle.get_result_async().add_done_callback(self._on_goal_result)

    def _on_goal_result(self, future):
        try:
            result = future.result()
        except Exception as error:
            self._finish_mission(f'Navigation result failed: {error}', failed=True)
            return
        if result.status != GoalStatus.STATUS_SUCCEEDED:
            name = self._targets[self._target_index][0]
            self._finish_mission(
                f'Navigation to {name} did not succeed.',
                failed=True,
            )
            return

        name = self._targets[self._target_index][0]
        self.get_logger().info(f'Arrived at {name}.')
        if self._target_index < 2:
            self._wait_timer = self.create_timer(
                5.0,
                self._on_wait_complete,
                callback_group=self._callback_group,
            )
            return
        self._finish_mission('Mission complete; robot returned to initial_pose.')

    def _on_wait_complete(self):
        self._wait_timer.cancel()
        self._wait_timer = None
        self._target_index += 1
        self._send_current_goal()

    def _finish_mission(self, message, failed=False):
        with self._lock:
            self._mission_active = False
        self._goal_handle = None
        if self._wait_timer is not None:
            self._wait_timer.cancel()
            self._wait_timer = None
        if failed:
            self.get_logger().error(message)
        else:
            self.get_logger().info(message)


def main(args=None):
    rclpy.init(args=args)
    node = MissionCommander()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
