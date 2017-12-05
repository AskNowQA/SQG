from copy import deepcopy
import torch.utils.data as data
import numpy as np
import torch
import utils


class QGDataset(data.Dataset):
    def __init__(self, num_classes, vocab_size):
        super(QGDataset, self).__init__()
        self.num_classes = num_classes

        self.questions = []
        self.queries = []
        self.labels = []
        self.size = 0
        self.vocab_size = vocab_size

    def counter_to_sparse(self, counters):
        try:
            counter = counters[0]
            zeros = np.zeros(len(counter[:, 0]), dtype=int)
            idx = torch.LongTensor([zeros, zeros, counter[:, 0]])
            values = torch.ByteTensor(counter[:, 1])
            for i in range(1, len(counters)):
                counter = counters[i]

                new_idx = torch.LongTensor(
                    [np.zeros(len(counter[:, 0]), dtype=int), [i] * len(counter[:, 0]), counter[:, 0]])
                idx = torch.cat((idx, new_idx), 1)

                values = torch.cat((values, torch.ByteTensor(counter[:, 1])), 0)
            return torch.sparse.ByteTensor(idx, values, torch.Size([1, len(counters), 3 * self.vocab_size]))
        except:
            return None

    def to_torch(self):
        self.questions = [self.counter_to_sparse(item) for item in self.questions]
        self.queries = [self.counter_to_sparse(item) for item in self.queries]
        self.labels = torch.Tensor(self.labels)

    def add(self, question, query, label):
        self.questions.append(question)
        self.queries.append(query)
        self.labels.append(label)
        self.size = len(self.questions)

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        question = deepcopy(self.questions[index])
        query = deepcopy(self.queries[index])
        label = deepcopy(self.labels[index])
        return question, query, label
