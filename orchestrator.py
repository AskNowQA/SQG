from common.graph.graph import Graph
from common.query.querybuilder import QueryBuilder
from parser.lc_quad import LC_Qaud
from sklearn.model_selection import train_test_split


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

    def generate_query(self, question, entities, relations, h1_threshold=None):
        ask_query = False
        sort_query = False
        count_query = False

        question_type = self.question_classifier.predict([question])
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

        return valid_walks, question_type
