import json, re
from qapair import QApair
from answer import Answer
from uri import Uri

class Qald:
	qald_6 = "/home/hamid/workspace/query_generation/data/QALD/6/data/qald-6-train-multilingual.json"
	qald_8 = "/home/hamid/workspace/query_generation/data/QALD/8/data/wikidata-train-7.json"

	def __init__(self, path):
		self.raw_data = []
		self.qapairs = []
		self.path = path

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):
		parser = QaldParser()
		for raw_row in self.raw_data["questions"]:
			self.qapairs.append(QApair(raw_row["question"], raw_row["answers"], raw_row["query"], parser))

	def print_pairs(self, n = -1):
		for item in self.qapairs[0:n]:
			print item
			print ""

class QaldParser:
	def parse_question(self, raw_question):
		for q in raw_question:
			if q["language"] == "en":
				return q["string"]

	def parse_sparql(self, raw_query):
		raw_query = raw_query["sparql"] if "sparql" in raw_query else ""
		uris = [Uri(raw_uri, self.parse_uri) for raw_uri in re.findall('(<[^>]*>|\?[^ ])',raw_query)]
		supported = not any(substring in raw_query for substring in ["UNION", "FILTER", "OFFSET", "HAVING", "LIMIT"])
		return raw_query, supported, uris

	def parse_answers(self, raw_answers):
		if len(raw_answers) > 0:
			if "boolean" in raw_answers[0]:
				return [Answer("boolean", raw_answers[0]["boolean"], self.parse_answer)]
			else:
				answers = []
				if len(raw_answers[0]["head"]["vars"]) > 0:
					answer_type = raw_answers[0]["head"]["vars"][0]
					for raw_answer in raw_answers[0]["results"]["bindings"]:
						answers.append(Answer(answer_type, raw_answer, self.parse_answer))
				return answers
		else:
			return []

	def parse_answer(self, answer_type, raw_answer):
		if answer_type == "boolean":
			return answer_type, str(raw_answer)
		else:
			if not answer_type in raw_answer:
				answer_type = "\"{}\"".format(answer_type)
			return raw_answer[answer_type]["type"], raw_answer[answer_type]["value"]

	def parse_uri(self, raw_uri):
		if raw_uri.find("/resource/") >= 0:
			return "?s", raw_uri
		elif raw_uri.find("/ontology/") >= 0 or raw_uri.find("/property/") >= 0:
			return "?p", raw_uri
		elif raw_uri.find("rdf-syntax-ns#type") >= 0:
			return "?t", raw_uri
		else:
			return "?u", raw_uri