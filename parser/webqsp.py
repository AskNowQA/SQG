import json, re
from common.qapair import QApair
from common.answer import Answer
from common.uri import Uri

class WebQSP:
	def __init__(self, path = "./data/WebQuestionsSP/WebQSP.train.json"):
		self.raw_data = []
		self.qapairs = []
		self.path = path

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):
		parser = QaldParser()
		for raw_row in self.raw_data["Questions"]:
			self.qapairs.append(QApair(raw_row["ProcessedQuestion"], raw_row["Parses"], raw_row["Parses"], raw_row, parser))

	def print_pairs(self, n = -1):
		for item in self.qapairs[0:n]:
			print item.sparql
			print ""

class QaldParser:
	def parse_question(self, raw_question):
		return raw_question

	def parse_sparql(self, raw_query):
		raw_query = raw_query[0]["Sparql"] if "Sparql" in raw_query[0] else ""
		raw_query = " ".join(raw_query.split("\n")[5:])
		raw_query = raw_query[:raw_query.rfind("}")]
		#remove comments from the sparql query
		for t in re.findall("\#[^\n]*", raw_query):
			raw_query = raw_query.replace(t, " ")
		uris = [Uri(raw_uri, self.parse_uri) for raw_uri in re.findall('(ns:[^ ]*|\?[^ ]*)', raw_query)]
		supported = not any(substring in raw_query.upper() for substring in ["EXISTS", "UNION", "FILTER"])
		return raw_query, supported, uris

	def parse_answers(self, raw_answers):
		answers = []
		for raw_answer in raw_answers[0]["Answers"]:
			answers.append(Answer(raw_answer["AnswerType"], raw_answer, self.parse_answer))
		return answers

	def parse_answer(self, answer_type, raw_answer):
		if answer_type == "Value":
			return answer_type, raw_answer["AnswerArgument"]
		else:
			return answer_type, raw_answer["EntityName"]

	def parse_uri(self, raw_uri):
		if raw_uri.find("ns:m.") >= 0:
			return "?s", raw_uri
		elif raw_uri.find("ns:") >= 0:
			return "?p", raw_uri
		else:
			return raw_uri, raw_uri