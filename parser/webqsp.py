import json
import re
from common.qapair import QApair
from common.uri import Uri
from common.answerrow import AnswerRow
from common.answer import Answer
from kb.freebase import Freebase
from answerparser import AnswerParser


class WebQSP:
    def __init__(self, path="./data/WebQuestionsSP/WebQSP.train.json"):
        self.raw_data = []
        self.qapairs = []
        self.path = path
        self.parser = WebQSPParser()

    def load(self, path=None):
        if path is None:
            path = self.path
        with open(path) as data_file:
            self.raw_data = json.load(data_file)

    def extend(self, path):
        self.load(path)
        self.parse()

    def parse(self):
        for raw_row in self.raw_data["Questions"]:
            self.qapairs.append(
                QApair(raw_row["ProcessedQuestion"], raw_row["Parses"][0]["Answers"], raw_row["Parses"][0]["Sparql"],
                       raw_row, raw_row["QuestionId"], self.parser))

    def print_pairs(self, n=-1):
        for item in self.qapairs[0:n]:
            print item.sparql
            print ""


class WebQSPParser(AnswerParser):
    def __init__(self):
        super(WebQSPParser, self).__init__(Freebase())

    def parse_question(self, raw_question):
        return raw_question

    def parse_sparql(self, raw_query):
        # remove comments from the sparql query
        for t in re.findall("\#[^\n]*", raw_query):
            raw_query = raw_query.replace(t, " ")

        raw_query = raw_query[raw_query.find("WHERE {") + 7:]
        if raw_query.split("\n")[2].startswith("FILTER"):
            raw_query = " ".join(raw_query.split("\n")[3:])
        else:
            raw_query = raw_query.replace("\n", " ")
        raw_query = raw_query[:raw_query.rfind("}")]
        uris = [Uri(raw_uri, Freebase.parse_uri) for raw_uri in re.findall('(ns:[^ ]*|\?[^ ]*)', raw_query)]
        supported = not any(substring in raw_query.upper() for substring in ["EXISTS", "UNION", "FILTER"])
        return raw_query, supported, uris

    def parse_answerset(self, raw_answers):
        answer_rows = []
        for raw_answer in raw_answers:
            answer_rows.append(AnswerRow(raw_answer, self.parse_answerrow))
        return answer_rows

    def parse_answerrow(self, raw_answerrow):
        answers = []
        answers.append(Answer(raw_answerrow["AnswerType"], raw_answerrow, self.parse_answer))
        return answers

    def parse_answer(self, answer_type, raw_answer):
        if answer_type == "Entity":
            return answer_type, Uri(self.kb.shorten_prefix() + raw_answer["AnswerArgument"], self.kb.parse_uri)
        elif answer_type == "Value":
            return answer_type, raw_answer["AnswerArgument"]
        else:
            return answer_type, Uri(raw_answer["EntityName"], self.kb.parse_uri)
