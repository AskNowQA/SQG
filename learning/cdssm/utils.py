from __future__ import division
from __future__ import print_function
from copy import deepcopy as copy
import math
import torch
import numpy as np


# mapping from scalar to vector
def map_label_to_target(label, num_classes):
    target = torch.zeros(1, num_classes)
    # if label == -1:
    #     target[0][0] = 1
    # else:
    #     target[0][1] = 1
    ceil = int(math.ceil(label))
    floor = int(math.floor(label))
    if ceil == floor:
        target[0][floor - 1] = 1
    else:
        target[0][floor - 1] = ceil - label
        target[0][ceil - 1] = label - floor
    return target


def accumu(l):
    total = 0
    for x in l:
        total += x
        yield total


def sparse_cat(l, size):
    output = l[0]
    for i in range(1, len(l)):
        output = np.concatenate([output, np.array(zip(l[i][:, 0] + (size * i), l[i][:, 1]))])

    return np.array(output)
