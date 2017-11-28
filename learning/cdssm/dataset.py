import os
from tqdm import tqdm
from copy import deepcopy
import torch
import torch.utils.data as data


class QGDataset(data.Dataset):
    def __init__(self, path, vocab, num_classes):
        super(QGDataset, self).__init__()
        self.vocab = vocab
        self.num_classes = num_classes

        self.questions = self.read_hashes(os.path.join(path, 'hashed_questions.txt'))
        self.queries = self.read_hashes(os.path.join(path, 'hashed_queries.txt'))

        self.labels = self.read_labels(os.path.join(path, 'sim.txt'))

        self.size = len(self.questions)

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        question = deepcopy(self.questions[index])
        query = deepcopy(self.queries[index])
        label = deepcopy(self.labels[index])
        return question, query, label

    def read_hashes(self, filename):
        with open(filename, 'r') as f:
            sentences = [self.read_hash(line) for line in tqdm(f.readlines())]
        return sentences

    def read_hash(self, line):
        indices = map(int, line.split())
        return torch.LongTensor(indices)

    def read_labels(self, filename):
        with open(filename, 'r') as f:
            labels = list(map(lambda x: float(x), f.readlines()))
            labels = torch.Tensor(labels)
        return labels
