import deepmk
import torch
import gym
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from deepmk.rl.algs import MonteCarloRL
from deepmk.rl.actors import GreedyActor
from deepmk.rl import train

# set up the training components
env = gym.make("CartPole-v0")
rlalg = MonteCarloRL(
    dataloader_kwargs={"shuffle": True, "batch_size": 4, "num_workers": 4},
    state_transform=torch.FloatTensor
)
model = nn.Linear(4, env.action_space.n)
actor = GreedyActor(model)
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
scheduler = lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

# train the model
model = train(env, rlalg, model, actor, optimizer, criterion=nn.MSELoss,
          reward_preproc=lambda x:x, scheduler=None, num_episodes=1000,
          val_every=20, val_episodes=10, verbose=1, plot=0,
          save_wts_to=None, save_model_to=None)