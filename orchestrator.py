from common.graph.graph import Graph
from common.query.querybuilder import QueryBuilder
from parser.lc_quad import LC_Qaud
from sklearn.model_selection import train_test_split


class Orchestrator:
    def __init__(self, question_classifier, parser):
        self.question_classifier = question_classifier
        self.parser = parser
        self.kb = parser.kb

        if not question_classifier.is_trained:
            self.__train_question_classifier()

    def __train_question_classifier(self):
        ds = LC_Qaud()
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

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.question_classifier.train(X_train, y_train)

    def generate_query(self, question, entities, relations):
        ask_query = False
        sort_query = False
        count_query = False

        question_type = self.question_classifier.predict([question])
        if question_type == 2:
            count_query = True
        elif question_type == 1:
            ask_query = True

        graph = Graph(self.kb)
        query_builder = QueryBuilder()
        graph.find_minimal_subgraph(entities, relations, ask_query, sort_query)
        return query_builder.to_where_statement(graph, self.parser.parse_queryresult, ask_query, count_query,
                                                sort_query)
