from copy import deepcopy
import torch.utils.data as data


class QGDataset(data.Dataset):
    def __init__(self, num_classes, vocab_size):
        super(QGDataset, self).__init__()
        self.num_classes = num_classes

        self.questions = []
        self.queries = []
        self.labels = []
        self.size = 0
        self.vocab_size = vocab_size

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
