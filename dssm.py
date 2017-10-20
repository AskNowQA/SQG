from common.preprocessing.wordhashing import WordHashing
from parser.webqsp import WebQSP
from lsa.dssm import DSSM
from lsa.dssm2 import DSSM2
import numpy as np
import tensorflow as tf

hashing = WordHashing()

ds = WebQSP()
ds.load()
ds.parse()
hashed_qapairs = {}
for qapair in ds.qapairs:
    hashed_question = hashing.hash(qapair.question.text)
    hashed_sparql = hashing.hash(qapair.sparql.where_clause)
    hashed_qapairs[qapair.id] = (hashed_question, hashed_sparql)

VOCAB_SIZE = 50000  # len(hashing.ids)
DATA_SIZE = len(ds.qapairs)
i = 0
questions = np.zeros([DATA_SIZE, VOCAB_SIZE])
sparqls = np.zeros([DATA_SIZE, VOCAB_SIZE])
for kv in hashed_qapairs.iteritems():
    question_unique_counts = np.unique(kv[1][0], return_counts=True)
    questions[i, question_unique_counts[0]] = question_unique_counts[1]

    sparql_unique_counts = np.unique(kv[1][1], return_counts=True)
    sparqls[i, sparql_unique_counts[0]] = sparql_unique_counts[1]
    i += 1

model = DSSM2()
model.train([questions, sparqls])
