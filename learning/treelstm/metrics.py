from copy import deepcopy

import torch


class Metrics():
    def __init__(self, num_classes):
        self.num_classes = num_classes

    def all(self, predictions, labels):
        return "\tPearson: {}\tMSE: {}, \tF1: {}".format(self.pearson(predictions, labels),
                                                         self.mse(predictions, labels),
                                                         self.f1(predictions, labels))

    def f1(self, predictions, labels):
        try:
            true = labels == predictions
            false = labels != predictions
            assert torch.sum(true) + torch.sum(false) == len(predictions)
            true_positive = torch.sum(true[labels == 1])
            true_negative = torch.sum(true[labels == -1])

            false_positive = torch.sum(false[labels == 1])
            false_negative = torch.sum(false[labels == -1])

            precision = 1.0 * true_positive / (true_positive + false_positive)
            recall = 1.0 * true_positive / (true_positive + false_negative)
            f1 = 2.0 * (precision * recall) / (precision + recall)
            return precision, recall, f1
        except:
            return 0, 0, 0

    def pearson(self, predictions, labels):
        x = deepcopy(predictions)
        y = deepcopy(labels)
        x = (x - x.mean()) / x.std()
        y = (y - y.mean()) / y.std()
        return torch.mean(torch.mul(x, y))

    def mse(self, predictions, labels):
        x = deepcopy(predictions)
        y = deepcopy(labels)
        return torch.mean((x - y) ** 2)
