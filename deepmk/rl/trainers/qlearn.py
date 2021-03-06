import copy
from collections import deque
from torch.utils.data import DataLoader
from deepmk.rl.trainers.trainer import Trainer
from deepmk.rl.dataloaders import LastStepLoader

__all__ = ["QLearn"]

class QLearn(Trainer):
    def __init__(self, qnet, optimizer, gamma=0.9, update_every=1,
                 train_after=0,
                 rldataloader=LastStepLoader()):
        self.qnet = qnet
        self.optimizer = optimizer
        self.tuples = []
        self.gamma = gamma
        self.update_every = update_every
        self.train_after = train_after
        self.rldataloader = rldataloader

        self.qnet_old = copy.deepcopy(qnet)
        self.num_steps = 0

    def trainstep(self, state, action, reward, next_state, done):
        # save the episode tuple
        tup = (state, action, reward, next_state, done)
        self.tuples.append(tup)

        if self.num_steps < self.train_after:
            self.num_steps += 1
            return

        # set the dataloader
        dataloader = self.rldataloader(self.tuples)

        # present the state and the target for the training
        if dataloader is not None:
            for s, a, r, snext, ep_done in dataloader:
                # calculate the loss based on the tuple
                snext_val = self.qnet_old.max_value(snext) * (1.0 - ep_done.float())
                train_target = r.float() + self.gamma * snext_val
                pred_target = self.qnet.value(s, a)

                loss = ((train_target.data - pred_target)**2).mean()

                # step the optimizer
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

        # update the num steps
        self.num_steps += 1
        # update the fixed models
        if self.num_steps % self.update_every == 0:
            self.qnet_old = copy.deepcopy(self.qnet)
