import logging
import os
import gym

from stable_baselines3.ppo.ppo import PPO
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback, CallbackList
from DrlPlatform.Models.abstract_server import AbstractServer
from Core.globals import EXIT_APP_EVENT
import gym.envs

class CustomCallback(BaseCallback):
    """
    A custom callback that derives from ``BaseCallback``.

    :param verbose: (int) Verbosity level 0: not output 1: info 2: debug
    """
    def __init__(self, verbose=0):
        super(CustomCallback, self).__init__(verbose)

    def _on_training_start(self) -> None:
        """
        This method is called before the first rollout starts.
        """
        pass

    def _on_rollout_start(self) -> None:
        """
        A rollout is the collection of environment interaction
        using the current policy.
        This event is triggered before collecting new samples.
        """
        pass

    def _on_step(self) -> bool:
        """
        This method will be called by the model after each call to `env.step()`.

        For child callback (of an `EventCallback`), this will be called
        when the event is triggered.

        :return: (bool) If the callback returns False, training is aborted early.
        """
        return True

    def _on_rollout_end(self) -> None:
        """
        This event is triggered before updating the policy.
        """
        logger= logging.getLogger(__name__)
        logger.error("ROLLOUT END")
        self.training_env.reset() # type: ignore

    def _on_training_end(self) -> None:
        """
        This event is triggered before exiting the `learn()` method.
        """
        logger= logging.getLogger(__name__)
        logger.error("TRAINING END")

MODE="train"
MODELS_ROOT = f"./Models/"
LOGS_ROOT = f"./Logs"

if not os.path.exists(MODELS_ROOT):
    raise ValueError("Models root directory does not exist")

if not os.path.exists(LOGS_ROOT):
    raise ValueError("Logs root directory does not exist")

def run_full_stack_agent(server: AbstractServer):
    logger = logging.getLogger(__name__)

    gym.envs.register(
        id='InvertedPendulumRT-v0',
        entry_point='UseCases.inverted_pendulum_rt:InvertedPendulumRT',
        max_episode_steps=512,
        reward_threshold=512,

    )
    gym.envs.register(
        id='SampleCartpole-v0',
        entry_point='UseCases.sample_cartpole:SampleCartpole',
        max_episode_steps=500,
        reward_threshold=500,
    )
    env: gym.Env = gym.make('InvertedPendulumRT-v0') #type: ignore
    env.env.env_server = server #type: ignore
    model = PPO('MlpPolicy',
                env,
                verbose=1,
                tensorboard_log=f"{LOGS_ROOT}/IPD_OL/PPO",
                n_steps=2048,
                batch_size=64,
                gae_lambda=0.95,
                gamma=0.99,
                n_epochs=20,
                ent_coef=0.0,
                learning_rate=2.5e-4,
                clip_range=0.2,
                device="cpu"
                )
    if MODE == "train":
        iteration = 0
        TOTAL_EPISODES = 20
        TIMESTEPS = 500_000
        while not EXIT_APP_EVENT.is_set():
            iteration += 1
            rollout_callback = CustomCallback()
            checkpoint_callback = CheckpointCallback(save_freq=5000, save_path=f'{MODELS_ROOT}/IPD_OL/PPO_{iteration}')
            callback = CallbackList([checkpoint_callback, rollout_callback])
            model.learn(total_timesteps=TIMESTEPS, callback = callback, tb_log_name=f"PPO", reset_num_timesteps=True)
            if iteration == TOTAL_EPISODES:
                break
    elif MODE == "infer":
        #model = model.load("./Models/IPD_OL/PPO_1/rl_model_180000_steps.zip")
        logger.warning("Operating the pendulum")
        obs = env.reset()
        while True:
            action, _state = model.predict(obs, deterministic=True)
            logger.warning(f"Action: {action}")
            obs, reward, done, info = env.step(action)
            logger.info(f"Observation: {obs}")
            if done:
                obs = env.reset()
    else:
        logger.error(f"unknown mode: {MODE}")
