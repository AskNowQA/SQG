import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable as Var


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
        inputs = inputs.float().transpose(1, 2)
        conv_vect = self.conv(inputs)
        conv_layer = F.tanh(conv_vect)
        max_pooling_vect = kmax_pooling(conv_layer, 2, 1).transpose(1, 2)
        max_pooling_layer = F.tanh(self.transformer(max_pooling_vect))
        return max_pooling_layer.resize(self.latent_size)


class Similarity(nn.Module):
    def __init__(self):
        super(Similarity, self).__init__()

    def forward(self, lvec, rvec):
        return F.cosine_similarity(lvec, rvec, dim=0)


class SimilarityCDSSM(nn.Module):
    def __init__(self, window_size, vocab_size, conv_size, latent_size):
        super(SimilarityCDSSM, self).__init__()
        self.cdssm = CDSSM(window_size, vocab_size, conv_size, latent_size)
        self.similarity = Similarity()

    def forward(self, linputs, rinputs):
        lstate = self.cdssm(linputs)
        rstate = self.cdssm(rinputs)
        output = self.similarity(lstate, rstate)
        return output
