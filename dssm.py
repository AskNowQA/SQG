import numpy as np
from sklearn.model_selection import train_test_split
from common.preprocessing.wordhashing import WordHashing
from parser.webqsp import WebQSP
from parser.lc_quad import LC_Qaud
from lsa.dssm import DSSM
from jerrl.jerrl import Jerrl


def preprocessing(qapairs):
    jerrl = Jerrl()
    hashing = WordHashing()
    hashed_qapairs = {}
    for qapair in qapairs:
        question = qapair.question.text
        query = qapair.sparql.raw_query
        counter = 0
        for item in jerrl.mentions(qapair):
            question = u"{0} {1} {2}".format(question[:item["start"]], str(counter), question[item["end"]:])
            query = query.replace(item["uri"].raw_uri, str(counter))
            counter += 1

        hashed_question = hashing.hash(question)
        hashed_sparql = hashing.hash(query)
        hashed_qapairs[qapair.id] = (hashed_question, hashed_sparql)

    VOCAB_SIZE = 50000  # len(hashing.ids)
    DATA_SIZE = len(qapairs)
    i = 0
    questions = np.zeros([DATA_SIZE, VOCAB_SIZE])
    sparqls = np.zeros([DATA_SIZE, VOCAB_SIZE])
    for kv in hashed_qapairs.iteritems():
        question_unique_counts = np.unique(kv[1][0], return_counts=True)
        questions[i, question_unique_counts[0]] = question_unique_counts[1]

        sparql_unique_counts = np.unique(kv[1][1], return_counts=True)
        sparqls[i, sparql_unique_counts[0]] = sparql_unique_counts[1]
        i += 1

    return questions, sparqls


ds = LC_Qaud()
ds.load()
ds.parse()

ds_train, ds_test, _, _ = train_test_split(ds.qapairs, np.ones([len(ds.qapairs), 1]), test_size=0.2)

# ds_train = ds.qapairs[:4000]
# ds_test = ds.qapairs[4000:]

model = DSSM(max_steps=10)
# questions, sparqls = preprocessing(ds_train)
# model.train([questions, sparqls])
# questions, queries = preprocessing(ds_test)
# model.test([questions, queries])
questions, sparqls = preprocessing(ds_test)
model.similarity(questions, sparqls)
