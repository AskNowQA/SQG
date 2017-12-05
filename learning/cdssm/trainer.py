from tqdm import tqdm
import torch
from torch.autograd import Variable as Var


class Trainer(object):
    def __init__(self, args, model, criterion, optimizer):
        super(Trainer, self).__init__()
        self.args = args
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.epoch = 0

    # helper function for training
    def train(self, dataset):
        self.model.train()
        self.optimizer.zero_grad()
        loss, k = 0.0, 0
        indices = torch.randperm(len(dataset))
        for idx in tqdm(range(len(dataset)), desc='Training epoch ' + str(self.epoch + 1) + ''):
            left, right, label = dataset[indices[idx]]
            linput, rinput = Var(left), Var(right)
            target = Var(torch.FloatTensor([label]))
            if self.args.cuda:
                linput, rinput = linput.cuda(), rinput.cuda()
                target = target.cuda()
            output = self.model(linput, rinput)
            err = self.criterion(output, target)
            loss += err.data[0]
            err.backward()
            k += 1
            if k % self.args.batchsize == 0:
                self.optimizer.step()
                self.optimizer.zero_grad()
        self.epoch += 1
        return loss / len(dataset)

    # helper function for testing
    def test(self, dataset):
        self.model.eval()
        loss = 0
        predictions = torch.zeros(len(dataset))
        indices = torch.arange(1, dataset.num_classes + 1)
        for idx in tqdm(range(len(dataset)), desc='Testing epoch  ' + str(self.epoch) + ''):
            left, right, label = dataset[indices[idx]]
            linput, rinput = Var(left, volatile=True), Var(right, volatile=True)
            target = Var(torch.FloatTensor([label]), volatile=True)
            if self.args.cuda:
                linput, rinput = linput.cuda(), rinput.cuda()
                target = target.cuda()
            output = self.model(linput, rinput)
            err = self.criterion(output, target)
            loss += err.data[0]
            output = output.data.squeeze().cpu()
            predictions[idx] = torch.dot(indices, torch.exp(output))
        return loss / len(dataset), predictions