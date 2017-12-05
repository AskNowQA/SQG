from __future__ import division
from __future__ import print_function

import os
import random
import logging
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable as Var

# IMPORT CONSTANTS
import Constants
# NEURAL NETWORK MODULES/LAYERS
from model import *
# DATA HANDLING CLASSES
# DATASET CLASS FOR QueryGenerator DATASET
from dataset import QGDataset
# METRICS CLASS FOR EVALUATION
from metrics import Metrics
# CONFIG PARSER
from config import parse_args
# TRAIN AND TEST HELPER FUNCTIONS
from trainer import Trainer


def main():
    global args
    args = parse_args()
    # global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s")
    # file logger
    fh = logging.FileHandler(os.path.join(args.save, args.expname) + '.log', mode='w')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # console logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # argument validation
    args.cuda = args.cuda and torch.cuda.is_available()
    if args.sparse and args.wd != 0:
        logger.error('Sparsity and weight decay are incompatible, pick one!')
        exit()
    logger.debug(args)
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    if args.cuda:
        torch.cuda.manual_seed(args.seed)
        torch.backends.cudnn.benchmark = True
    if not os.path.exists(args.save):
        os.makedirs(args.save)

    train_dir = os.path.join(args.data, 'train/')
    dev_dir = os.path.join(args.data, 'dev/')
    test_dir = os.path.join(args.data, 'test/')

    # load dataset splits
    train_file = os.path.join(args.data, 'dataset_train.pth')
    if os.path.isfile(train_file):
        train_dataset = torch.load(train_file)
        train_dataset.to_torch()
    else:
        train_dataset = QGDataset(train_dir, args.num_classes)
        torch.save(train_dataset, train_file)
    logger.debug('==> Size of train data   : %d ' % len(train_dataset))
    dev_file = os.path.join(args.data, 'dataset_dev.pth')
    if os.path.isfile(dev_file):
        dev_dataset = torch.load(dev_file)
        dev_dataset.to_torch()
    else:
        dev_dataset = QGDataset(dev_dir, args.num_classes)
        torch.save(dev_dataset, dev_file)
    logger.debug('==> Size of dev data     : %d ' % len(dev_dataset))
    test_file = os.path.join(args.data, 'dataset_test.pth')
    if os.path.isfile(test_file):
        test_dataset = torch.load(test_file)
        test_dataset.to_torch()
    else:
        test_dataset = QGDataset(test_dir, args.num_classes)
        torch.save(test_dataset, test_file)
    logger.debug('==> Size of test data    : %d ' % len(test_dataset))
    # assert train_dataset.vocab_size == test_dataset.vocab_size

    vocab_size = train_dataset.vocab_size
    # initialize model, criterion/loss_function, optimizer
    model = SimilarityCDSSM(
        args.window_size,
        vocab_size,
        args.conv_size,
        args.latent_size)
    criterion = nn.KLDivLoss()  # torch.nn.CrossEntropyLoss()   # nn.HingeEmbeddingLoss()

    if args.cuda:
        model.cuda(), criterion.cuda()
    else:
        torch.set_num_threads(4)
    logger.info("number of available cores: {}".format(torch.get_num_threads()))
    if args.optim == 'adam':
        optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wd)
    elif args.optim == 'adagrad':
        optimizer = optim.Adagrad(model.parameters(), lr=args.lr, weight_decay=args.wd)
    elif args.optim == 'sgd':
        optimizer = optim.SGD(model.parameters(), lr=args.lr, weight_decay=args.wd)
    metrics = Metrics(args.num_classes)

    checkpoint_filename = '%s.pt' % os.path.join(args.save, args.expname)
    if args.mode == "test":
        checkpoint = torch.load(checkpoint_filename)
        model.load_state_dict(checkpoint['model'])
        args.epochs = 1

    # create trainer object for training and testing
    trainer = Trainer(args, model, criterion, optimizer)

    for epoch in range(args.epochs):
        if args.mode == "train":
            train_loss = trainer.train(train_dataset)
            train_loss, train_pred = trainer.test(train_dataset)
            logger.info(
                '==> Epoch {}, Train \tLoss: {} {}'.format(epoch, train_loss,
                                                           metrics.all(train_pred, train_dataset.labels)))
            checkpoint = {'model': trainer.model.state_dict(), 'optim': trainer.optimizer,
                          'args': args, 'epoch': epoch}
            torch.save(checkpoint, checkpoint_filename)

        dev_loss, dev_pred = trainer.test(dev_dataset)
        test_loss, test_pred = trainer.test(test_dataset)
        logger.info(
            '==> Epoch {}, Dev \tLoss: {} {}'.format(epoch, dev_loss, metrics.all(dev_pred, dev_dataset.labels)))
        logger.info(
            '==> Epoch {}, Test \tLoss: {} {}'.format(epoch, test_loss, metrics.all(test_pred, test_dataset.labels)))


if __name__ == "__main__":
    main()
