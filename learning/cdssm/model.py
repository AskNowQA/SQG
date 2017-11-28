import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable as Var
from Constants import *


def kmax_pooling(x, dim, k):
    index = x.topk(k, dim=dim)[1].sort(dim=dim)[0]
    return x.gather(dim, index)


class CDSSM(nn.Module):
    def __init__(self, window_size, vocab_size, conv_size, latent_size):
        super(CDSSM, self).__init__()
        self.latent_size = latent_size
        self.conv = nn.Conv1d(window_size * vocab_size, conv_size, 1)
        self.transformer = nn.Linear(conv_size, latent_size)

    def forward(self, inputs):
        conv_vect = self.conv(inputs)
        conv_layer = F.tanh(conv_vect)
        max_pooling_vect = kmax_pooling(conv_layer, 2, 1)
        max_pooling_layer = F.tanh(self.transformer(max_pooling_vect))
        return max_pooling_layer.resize(self.latent_size)


class Similarity(nn.Module):
    def __init__(self):
        super(Similarity, self).__init__()

    def forward(self, lvec, rvec):
        return F.cosine_similarity(lvec, rvec)


class SimilarityCDSSM(nn.Module):
    def __init__(self):
        super(SimilarityCDSSM, self).__init__()
        self.cdssm = CDSSM()
        self.similarity = Similarity()

    def forward(self, left, linputs, right, rinputs):
        linputs = self.emb(linputs)
        rinputs = self.emb(rinputs)
        lstate, lhidden = self.cdssm(left, linputs)
        rstate, rhidden = self.cdssm(right, rinputs)
        output = self.similarity(lstate, rstate)
        return output
