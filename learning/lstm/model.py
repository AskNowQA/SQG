import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable as Var

import Constants


# module for distance-angle similarity
class DASimilarity(nn.Module):
    def __init__(self, mem_dim, hidden_dim, num_classes):
        super(DASimilarity, self).__init__()
        self.mem_dim = mem_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        self.wh = nn.Linear(2 * self.mem_dim, self.hidden_dim)
        self.wp = nn.Linear(self.hidden_dim, self.num_classes)

    def forward(self, lvec, rvec):
        mult_dist = torch.mul(lvec, rvec)
        abs_dist = torch.abs(torch.add(lvec, -rvec))
        vec_dist = torch.cat((mult_dist, abs_dist), 1)

        out = F.sigmoid(self.wh(vec_dist))
        out = F.log_softmax(self.wp(out))
        return out


# module for cosine similarity
class CosSimilarity(nn.Module):
    def __init__(self, mem_dim):
        super(CosSimilarity, self).__init__()
        self.cos = nn.CosineSimilarity(dim=mem_dim)

    def forward(self, lvec, rvec):
        out = self.cos(lvec, rvec)
        out = torch.autograd.Variable(torch.FloatTensor([[1 - out.data[0], out.data[0]]]), requires_grad=True)
        if torch.cuda.is_available():
            out = out.cuda()
        return F.log_softmax(out)


# putting the whole model together
class SimilarityLSTM(nn.Module):
    def __init__(self, vocab_size, in_dim, mem_dim, similarity, sparsity):
        super(SimilarityLSTM, self).__init__()
        self.emb = nn.Embedding(vocab_size, in_dim, padding_idx=Constants.PAD, sparse=sparsity)
        self.lstm = nn.LSTM(input_size=in_dim, hidden_size=mem_dim)
        self.similarity = similarity

    def forward(self, linputs, rinputs):
        linputs = self.emb(linputs)
        rinputs = self.emb(rinputs)

        lhidden = None
        for item in linputs:
            lstate, lhidden = self.lstm(item.view(1, -1), lhidden)
        rhidden = None
        for item in rinputs:
            rstate, rhidden = self.lstm(item.view(1, -1), rhidden)

        # output = self.similarity(lstate, rstate)
        output = torch.exp(-torch.norm((lstate - rstate), 1))
        return output
