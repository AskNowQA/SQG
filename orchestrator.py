from common.graph.graph import Graph
from common.query.querybuilder import QueryBuilder
from parser.lc_quad import LC_Qaud
from sklearn.model_selection import train_test_split

import os
import torch
import torch.nn as nn
import torch.optim as optim
from learning.treelstm.model import *
from learning.treelstm.vocab import Vocab
from learning.treelstm.metrics import Metrics
from learning.treelstm.utils import load_word_vectors, build_vocab
from learning.treelstm.config import parse_args
from learning.treelstm.trainer import Trainer
from learning.treelstm.dataset import QGDataset
import learning.treelstm.scripts.preprocess_lcquad as preprocess_lcquad
from common.container.uri import Uri
from common.container.linkeditem import LinkedItem
from parser.lc_quad import LC_QaudParser


class Struct(object): pass


class Orchestrator:
    def __init__(self, question_classifier, double_relation_classifer, parser, auto_train=True):
        self.question_classifier = question_classifier
        self.double_relation_classifer = double_relation_classifer
        self.parser = parser
        self.kb = parser.kb
        self.X_train, self.X_test, self.y_train, self.y_test = [], [], [], []

        if auto_train and not question_classifier.is_trained:
            self.train_question_classifier()

        if auto_train and double_relation_classifer is not None and not double_relation_classifer.is_trained:
            self.train_double_relation_classifier()

    def prepare_question_classifier_dataset(self, file_path=None):
        if file_path is None:
            ds = LC_Qaud()
        else:
            ds = LC_Qaud(file_path)
        ds.load()
        ds.parse()

        X = []
        y = []
        for qapair in ds.qapairs:
            X.append(qapair.question.text)
            if "COUNT(" in qapair.sparql.raw_query:
                y.append(2)
            elif "ASK WHERE" in qapair.sparql.raw_query:
                y.append(1)
            else:
                y.append(0)

        return X, y

    def train_question_classifier(self, file_path=None, test_size=0.2):
        X, y = self.prepare_dataset(file_path)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size,
                                                                                random_state=42)
        return self.question_classifier.train(self.X_train, self.y_train)

    def prepare_double_relation_classifier_dataset(self, file_path=None):
        if file_path is None:
            ds = LC_Qaud()
        else:
            ds = LC_Qaud(file_path)
        ds.load()
        ds.parse()

        X = []
        y = []
        for qapair in ds.qapairs:
            X.append(qapair.question.text)
            relation_uris = [u for u in qapair.sparql.uris if u.is_ontology() or u.is_type()]
            if len(relation_uris) != len(set(relation_uris)):
                y.append(1)
            else:
                y.append(0)

        return X, y

    def train_question_classifier(self, file_path=None, test_size=0.2):
        X, y = self.prepare_question_classifier_dataset(file_path)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size,
                                                                                random_state=42)
        return self.question_classifier.train(self.X_train, self.y_train)

    def train_double_relation_classifier(self, file_path=None, test_size=0.2):
        X, y = self.prepare_double_relation_classifier_dataset(file_path)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size,
                                                                                random_state=42)
        return self.double_relation_classifer.train(self.X_train, self.y_train)

    def rank(self, args, question, generated_queries):
        if len(generated_queries) == 0:
            return []
        # Load the model
        checkpoint_filename = '%s.pt' % os.path.join(args.save, args.expname)
        dataset_vocab_file = os.path.join(args.data, 'dataset.vocab')
        # metrics = Metrics(args.num_classes)
        vocab = Vocab(filename=dataset_vocab_file,
                      data=[Constants.PAD_WORD, Constants.UNK_WORD, Constants.BOS_WORD, Constants.EOS_WORD])
        similarity = DASimilarity(args.mem_dim, args.hidden_dim, args.num_classes)
        model = SimilarityTreeLSTM(
            vocab.size(),
            args.input_dim,
            args.mem_dim,
            similarity,
            args.sparse)
        criterion = nn.KLDivLoss()
        optimizer = optim.Adagrad(model.parameters(), lr=args.lr, weight_decay=args.wd)
        emb_file = os.path.join(args.data, 'dataset_embed.pth')
        if os.path.isfile(emb_file):
            emb = torch.load(emb_file)
        model.emb.weight.data.copy_(emb)
        checkpoint = torch.load(checkpoint_filename, map_location=lambda storage, loc: storage)
        model.load_state_dict(checkpoint['model'])
        trainer = Trainer(args, model, criterion, optimizer)

        # Prepare the dataset
        json_data = [{"id": "test", "question": question,
                      "generated_queries": [{"query": " .".join(query["where"]), "correct": False} for query in
                                            generated_queries]}]
        output_dir = "./output/tmp"
        preprocess_lcquad.split(json_data, output_dir, self.parser)

        lib_dir = './learning/treelstm/lib/'
        classpath = ':'.join([
            lib_dir,
            os.path.join(lib_dir, 'stanford-parser/stanford-parser.jar'),
            os.path.join(lib_dir, 'stanford-parser/stanford-parser-3.5.1-models.jar')])

        preprocess_lcquad.parse(output_dir, cp=classpath)
        test_dataset = QGDataset(output_dir, vocab, args.num_classes)

        test_loss, test_pred = trainer.test(test_dataset)
        return test_pred

    def generate_query(self, question, entities, relations, h1_threshold=None):
        ask_query = False
        sort_query = False
        count_query = False

        question_type = 0
        if self.question_classifier is not None:
            self.question_classifier.predict([question])
        if question_type == 2:
            count_query = True
        elif question_type == 1:
            ask_query = True

        double_relation = False
        if self.double_relation_classifer is not None:
            double_relation = self.double_relation_classifer.predict([question])
            if double_relation == 1:
                double_relation = True

        graph = Graph(self.kb)
        query_builder = QueryBuilder()
        graph.find_minimal_subgraph(entities, relations, double_relation=double_relation, ask_query=ask_query,
                                    sort_query=sort_query, h1_threshold=h1_threshold)
        valid_walks = query_builder.to_where_statement(graph, self.parser.parse_queryresult, ask_query=ask_query,
                                                       count_query=count_query, sort_query=sort_query)

        args = Struct()
        base_path = "./learning/treelstm/"
        args.save = os.path.join(base_path, "checkpoints/")
        args.expname = "lc_quad"
        args.mem_dim = 150
        args.hidden_dim = 50
        args.num_classes = 2
        args.input_dim = 300
        args.sparse = ""
        args.lr = 0.01
        args.wd = 1e-4
        args.data = os.path.join(base_path, "data/lc_quad/")
        args.cuda = False
        scores = self.rank(args, question, valid_walks)
        for idx, item in enumerate(valid_walks):
            item["confidence"] = scores[idx] - 1

        return valid_walks, question_type


if __name__ == "__main__":
    args = Struct()
    base_path = "./learning/treelstm/"
    args.save = os.path.join(base_path, "checkpoints/")
    args.expname = "lc_quad"
    args.mem_dim = 150
    args.hidden_dim = 50
    args.num_classes = 2
    args.input_dim = 300
    args.sparse = ""
    args.lr = 0.01
    args.wd = 1e-4
    args.data = os.path.join(base_path, "data/lc_quad/")
    args.cuda = False

    parser = LC_QaudParser()
    kb = parser.kb
    o = Orchestrator(None, None, parser, False)
    raw_entities = [{"surface": "", "uris": [{"confidence": 1, "uri": "http://dbpedia.org/resource/Bill_Finger"}]}]
    entities = []
    for item in raw_entities:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        entities.append(LinkedItem(item["surface"], uris))

    raw_relations = [{"surface": "", "uris": [{"confidence": 1, "uri": "http://dbpedia.org/ontology/creator"}]},
                     {"surface": "", "uris": [{"confidence": 1, "uri": "http://dbpedia.org/ontology/ComicsCharacter"}]}]

    relations = []
    for item in raw_relations:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        relations.append(LinkedItem(item["surface"], uris))

    question = "Which comic characters are painted by Bill Finger?"
    # generated_queries = o.generate_query(question, entities, relations)[0]
    # print generated_queries
    generated_queries = [
        {'where': [u'?u_0 <http://dbpedia.org/ontology/creator> <http://dbpedia.org/resource/Bill_Finger>',
                   u'?u_0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/ComicsCharacter>']},
        {'where': [u'?u_0 <http://dbpedia.org/ontology/ComicsCharacter> <http://dbpedia.org/resource/Bill_Finger>',
                   u'?u_0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/creator>']}
    ]
    scores = o.rank(args, question, generated_queries)
    print scores
