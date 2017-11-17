from linker.jerrl import Jerrl
from common.preprocessing.wordhashing import WordHashing
import numpy as np


class Preprocessor:
    @staticmethod
    def qapair_to_hash(question_answer_uris):
        jerrl = Jerrl()
        hashing = WordHashing()
        hashed_qapairs = {}
        for data_item in question_answer_uris:
            question = data_item["question"]
            query = data_item["query"]
            counter = 0
            for item in jerrl.find_mentions(question, data_item["uris"]):
                question = u"{0} {1} {2}".format(question[:item["start"]], str(counter), question[item["end"]:])
                query = query.replace(item["uri"].raw_uri, str(counter))
                counter += 1

            hashed_question = hashing.hash(question)
            hashed_sparql = hashing.hash(query)
            hashed_qapairs[data_item["id"]] = (hashed_question, hashed_sparql)

        VOCAB_SIZE = 50000  # len(hashing.ids)
        DATA_SIZE = len(question_answer_uris)
        i = 0
        questions = np.zeros([DATA_SIZE, VOCAB_SIZE])
        sparqls = np.zeros([DATA_SIZE, VOCAB_SIZE])
        ids = []
        for kv in hashed_qapairs.iteritems():
            question_unique_counts = np.unique(kv[1][0], return_counts=True)
            questions[i, question_unique_counts[0]] = question_unique_counts[1]

            sparql_unique_counts = np.unique(kv[1][1], return_counts=True)
            sparqls[i, sparql_unique_counts[0]] = sparql_unique_counts[1]
            ids.append(kv[0])
            i += 1

        return questions, sparqls, ids
