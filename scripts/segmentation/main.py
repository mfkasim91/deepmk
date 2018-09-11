import os
import numpy as np
import torch
import deepmk
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import deepmk.datasets as mkdatasets
import deepmk.models as mkmodels
import deepmk.transforms as mktransforms
import deepmk.criteria as mkcriteria

name = "01-coco"

# transform the image to tensor
coco_both_transform = transforms.Compose([
    mktransforms.RandomCropTensor(320, pad_if_needed=True)
])
coco_img_transform = transforms.Compose([
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
fdir = os.path.dirname(os.path.abspath(__file__))
coco_dir = os.path.join(fdir, "..", "..", "dataset", "coco")
# get the coco dataset
coco = {
    x: mkdatasets.CocoDetection(os.path.join(coco_dir, "%s2017"%x),
        os.path.join(coco_dir, "annotations", ("instances_%s2017.json"%x)),
        both_transform=coco_both_transform,
        img_transform=coco_img_transform)
    for x in ["train", "val"]
}
# dataloader
dataloader = {
    x: DataLoader(coco[x], batch_size=16, shuffle=True, num_workers=16)
    for x in ["train", "val"]
}

# load the model
fcn = mkmodels.fcn8(coco["train"].ncategories)

criteria = {
    # criterion: binary cross entropy with logits loss
    # (i.e. classification done per-pixel)
    "train": nn.BCEWithLogitsLoss(),
    "val": mkcriteria.IoU()
}

# the learning process
optimizer = optim.SGD(fcn.parameters(), lr=0.001, momentum=0.9)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

# deepmk.spv.train(fcn, dataloader, criteria, optimizer,
#     scheduler=scheduler, plot=0, save_wts_to=name+".pkl", verbose=2)

deepmk.spv.validate(fcn, dataloader["val"], criteria["val"],
    load_wts_from=name+".pkl", verbose=2)
