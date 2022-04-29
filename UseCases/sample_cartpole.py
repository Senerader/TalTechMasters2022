import logging
import numpy as np
import math
import coloredlogs
import gym
import gym.envs
from math import atan2
from gym.spaces import Discrete, Box
from DrlPlatform import PlatformEnvironment, UdpServer

class SampleCartpole(PlatformEnvironment):
    """
    Custom Simulink env with non-realtime execution
    """
    def __init__(self):
        super(SampleCartpole, self).__init__()
        self._logger = logging.getLogger(__name__)
        sin_max = 1
        cos_max = 1
        velocity_max = np.finfo(np.float32).max
        high = np.array(
            [
                sin_max,
                cos_max,
                velocity_max
            ],
            dtype=np.float32,
        )
        self.observation_space = Box(-high, high, dtype=np.float32) #type: ignore
        self.action_space = Discrete(3)
        self.angle_threshold = 12 * 2 * math.pi / 360
        self.vel_threshold = 10

    def reset(self):
        self.done = False
        self._logger.warning("ENV RESET")
        self.env_server.send_payload([0, 1],">dd")
        payload = self.env_server.receive_payload(">ddd")
        sin, cos, vel = \
            payload[0], payload[1], payload[2]
        return np.asarray([sin, cos, vel])

    def step(self, action):
        assert action in [0, 1, 2], action
        if action == 0:
            force = -2
        elif action == 1:
            force = 0
        elif action == 2:
            force = 2
        else:
            raise ValueError(f"Unknown action {action}")

        self.env_server.send_payload([force, 0], ">dd")
        payload = self.env_server.receive_payload(">ddd")
        sin, cos, vel = \
            payload[0], payload[1], payload[2]
        angle = atan2(sin, cos)
        self._logger.info(f"Angle: {angle}")
        self.done = bool(
            vel < -self.vel_threshold
            or vel > self.vel_threshold
        )
        #  full range reward structure
        self.reward = -1 * (abs(angle/math.pi) -1)
        self._logger.info(f"Reward: {self.reward}")
        return np.array([sin, cos, vel], dtype=np.float32), self.reward, self.done, {}

if __name__ == "__main__":
    coloredlogs.install(level="INFO")
    logging.getLogger().setLevel(logging.INFO)
    try:
        from stable_baselines3.ppo.ppo import PPO
        from stable_baselines3.common.callbacks import CheckpointCallback
    except:
        print("To execute, this code must have Stable-Baselines3 installed")
    env_server = UdpServer(
        "127.0.0.1",
        16385,
        "127.0.0.1",
        16384
    )
    env_server.start_server()
    gym.envs.register(
        id='SampleCartpole-v0',
        entry_point='sample_cartpole:SampleCartpole',
        max_episode_steps=500,
        reward_threshold=500,
    )
    env = gym.make('SampleCartpole-v0') #type: ignore
    env.env.env_server = env_server #type:ignore
    model = PPO('MlpPolicy', #type: ignore
                env,
                verbose=1,
                tensorboard_log=f"Logs/Test/SampleCartpole/PPO",
                device="cpu"
                )
    try:
        #checkpoint_callback = CheckpointCallback(save_freq=5000, save_path=f'Models/TestModels/SampleCartpole/PPO') #type: ignore
        #model.learn(total_timesteps=500_000, callback = checkpoint_callback, tb_log_name=f"PPO")
        model = model.load("./Models/TestModels/SampleCartpole/PPO/rl_model_420000_steps.zip")
        obs = env.reset()
        while True:
            action, _state = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            if done:
                obs = env.reset()
    finally:
        env_server.close_server()