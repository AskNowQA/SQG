from copy import deepcopy
from sklearn.metrics import precision_recall_fscore_support
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
            y_true = list(labels)
            y_pred = map(round, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro')
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
