import logging
from typing import Optional
import gym
import math
import numpy as np
import time
from gym import spaces
from DrlPlatform import PlatformEnvironment

class InvertedPendulumRT(PlatformEnvironment):
    """Custom class that represents the Pendulum environment
    Limits were taken based on INTECO documentation of Fuzzy controller
    Observation:
        Type: Box(5)
        Num     Observation               Min                     Max
        0       Cart Position             -5                      5
        1       Cart Velocity             -inf                    inf
        2       Sine of Angle             -1                      1
        3       Cosine of Angle           -1                      1
        4       Pole Angular Velocity     -inf                    inf
    Actions:
        Type: Box(1)
        Num   Action                      Min                     Max
        0     PWM                         -0.5                    0.5

    """

    def __init__ (self):
        super(InvertedPendulumRT, self).__init__()
        self._logger = logging.getLogger(__name__)
        self.cart_pos_max = 1
        self.cart_vel_max = np.finfo(np.float32).max
        self.pole_sine_max = 1
        self.pole_cosine_max = 1
        self.pole_angular_vel_max = np.finfo(np.float32).max
        high = np.array(
            [
                self.cart_pos_max,
                self.cart_vel_max,
                self.pole_sine_max,
                self.pole_cosine_max,
                self.pole_angular_vel_max
            ],
            dtype=np.float32,
        )
        self.observation_space = spaces.Box(-high, high, dtype=np.float32) #type: ignore
        self.action_space = spaces.Box(
            low=-0.5, high=0.5, shape=(1,), dtype=np.float32
        )
        self.total_reward = 0.0
        self.done = False
        self.cart_vel_threshold = 3
        self.pole_vel_threshold = 15
        self.cart_pos_threshold = 0.7
        # Historical data
        self.previous_cart_pose = None
        self.previous_cart_velocity = None
        self.previous_pend_pose = None
        self.previous_pend_vel = None
        self.previous_action = None

    def _receive_payload(self):
        # Returns cart_pose, cart_vel, pend_
        payload = self.env_server.receive_payload(">dddd")
        formatted_payload = self.format_payload(payload)
        cart_pose, cart_vel, pendulum_pose, pendulum_vel = \
            formatted_payload[0], formatted_payload[1], formatted_payload[2], formatted_payload[3]
        if not (self.previous_cart_pose and self.previous_cart_velocity \
                and self.previous_pend_pose and self.previous_pend_vel):
                self.previous_cart_pose = cart_pose
                self.previous_cart_velocity = cart_vel
                self.previous_pend_pose = pendulum_pose
                self.previous_pend_vel = pendulum_vel
        else:
            # Noise detection
            while True:
                if abs(self.previous_cart_pose - cart_pose) > self.cart_pos_threshold or \
                abs(self.previous_pend_vel - pendulum_vel) > self.pole_vel_threshold or \
                abs(self.previous_cart_velocity - cart_vel) > self.cart_vel_threshold:
                    self._logger.warning("Detected noise")
                    payload = self.env_server.receive_payload(">dddd")
                    formatted_payload = self.format_payload(payload)
                    cart_pose, cart_vel, pendulum_pose, pendulum_vel = \
                        formatted_payload[0], formatted_payload[1], formatted_payload[2], formatted_payload[3]
                    continue
                else:
                    break
        self.previous_cart_pose = cart_pose
        self.previous_cart_velocity = cart_vel
        self.previous_pend_pose = pendulum_pose
        self.previous_pend_vel = pendulum_vel
        return cart_pose, cart_vel, pendulum_pose, pendulum_vel

    
    def step(self, action):
        # Negative reward for a step
        info = {}
        # Sending action through env server
        self.previous_action = action
        self.env_server.send_payload(
            payload=[action, 0],
            sending_mask=">dd"
        )
        time.sleep(0.031)
        cart_pose, cart_vel, pendulum_pose, pendulum_vel = \
            self._receive_payload()
        pendulum_sine = math.sin(pendulum_pose)
        pendulum_cosine = math.cos(pendulum_pose)
        self._logger.info(f"Pendulum pose: {pendulum_pose}\nPendulum vel: {pendulum_vel}\nCart pose: {cart_pose}\nCart vel: {cart_vel}")
        # Cart reward calculation
        if not self.done:    
            self.done = bool(
                pendulum_vel < -self.pole_vel_threshold
                or pendulum_vel > self.pole_vel_threshold
            )
            if self.done:
                self.reward = -30
        if not self.done:
            self.done = bool(
                cart_vel < -self.cart_vel_threshold
                or cart_vel > self.cart_vel_threshold
            )
            if self.done:
                self.reward = -30
        if not self.done:
            self.done = bool(
                cart_pose < -self.cart_pos_threshold
                or cart_pose > self.cart_pos_threshold
            )
            if self.done:
                self.reward = -50
        # self.reward = -((((pendulum_pose + np.pi) % (2 * np.pi)) - np.pi) ** 2 \
        #             + 0.1 * pendulum_vel ** 2 + 0.01 * (cart_vel ** 2))
        self.reward = self._pendulum_pose_reward(pendulum_pose) * \
                      self._pendulum_velocity_reward(pendulum_vel) * \
                      (self._cart_pose_reward(cart_pose) + \
                      self._cart_velocity_reward(cart_vel))
        self.total_reward += self.reward
        formatted_payload = np.array([cart_pose, cart_vel, pendulum_sine, pendulum_cosine, pendulum_vel], dtype=np.float32)
        # Return the result
        self._logger.info(f"Reward: {self.reward}")
        return formatted_payload, self.reward, self.done, info
    
    def _pendulum_pose_reward(self, angle: float):
        # return 1 at top pose
        return -1 * (abs(angle/math.pi) -1)
    
    def _pendulum_velocity_reward(self, velocity: float):
        # return 1 at zero velocity
        return (self.pole_vel_threshold - abs(velocity))/self.pole_vel_threshold

    def _cart_pose_reward(self, pose: float):
        # return 1 at zero pose
        return (self.cart_pos_max - abs(pose))/self.cart_pos_max * 0.75

    def _cart_velocity_reward(self, velocity):
        # return 1 at zero velocity
        return (self.cart_vel_threshold - abs(velocity))/self.cart_vel_threshold * 0.25


    def reset(self) -> np.ndarray:
        self.counter = 0
        self.total_reward = 0
        self.done = False
        self.previous_cart_pose = None
        self.previous_cart_velocity = None
        self.previous_pend_pose = None
        self.previous_pend_vel = None
        self._logger.warning("ENV RESET")
        if not self.previous_action:
            self.previous_action = 0
        self.env_server.send_payload([-self.previous_action, 1],
                        sending_mask=">dd")
        self.previous_action = None
        time.sleep(0.031)
        payload = self.env_server.receive_payload(">dddd")
        formatted_payload = self.format_payload(payload)
        while not self._is_env_reset(formatted_payload):
            self.env_server.send_payload([0, 1],
                        sending_mask=">dd")
            time.sleep(0.031)
            payload = self.env_server.receive_payload(">dddd")
            formatted_payload = self.format_payload(payload)
        self._logger.warning("ENV RESET DONE")
        cart_pose, cart_vel, pendulum_pose, pendulum_vel = \
            formatted_payload[0], formatted_payload[1], formatted_payload[2], formatted_payload[3]
        self._logger.info(f"Pendulum pose: {pendulum_pose}\nPendulum vel: {pendulum_vel}\nCart pose: {cart_pose}\nCart vel: {cart_vel}")
        pendulum_sine = math.sin(pendulum_pose)
        pendulum_cosine = math.cos(pendulum_pose)
        formatted_payload = np.array([cart_pose, cart_vel, pendulum_sine, pendulum_cosine, pendulum_vel], dtype=np.float32)
        return formatted_payload
    
    def format_payload(self, payload) -> np.ndarray:
        """
        Formatting payload which is going to be sent to training agent
        """
        formatted_payload = np.array(payload, dtype=np.float32)
        # Array poses:
        # 1. Pendulum position
        # 2. Pendulum velocity
        # 3. Cart position
        # 4. Cart velocity
        pendulum_pose, pendulum_velocity, cart_pose, cart_velocity = \
            formatted_payload[0], formatted_payload[1], formatted_payload[2], formatted_payload[3]
        return np.array([cart_pose, cart_velocity, pendulum_pose, pendulum_velocity], dtype=np.float32)

    def _is_env_reset(self, formatted_payload) -> bool:
        """
        Check if env has been reset
        """
        cart_pose, cart_velocity, pendulum_pose, pendulum_velocity = \
            formatted_payload[0], formatted_payload[1], formatted_payload[2], formatted_payload[3]
        counter = 0
        is_reset = True
        while counter <= 5:
            is_reset = is_reset * (abs(pendulum_pose) > 2.9) \
            and (abs(pendulum_velocity) < 1) \
            and ((abs(cart_velocity) < 0.2)) \
            and (abs(cart_pose) < 0.1)
            counter += 1
        return is_reset
