import json, re
from common.qapair import QApair
from common.answer import Answer
from common.uri import Uri
from dbpedia.dbpedia import DBpedia


class LC_Qaud_Linked:	
	def __init__(self, path = "./data/LC-QUAD/linked.json"):
		self.raw_data = []
		self.qapairs = []
		self.path = path
		self.parser = LC_Qaud_LinkedParser()

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):		
		for raw_row in self.raw_data:
			self.qapairs.append(QApair(raw_row["question"], raw_row.get("answers"), raw_row["sparql_query"], raw_row, self.parser))

	def print_pairs(self, n = -1):
		for item in self.qapairs[0:n]:
			print item
			print ""


class LC_Qaud_LinkedParser:
	def parse_question(self, raw_question):
		return raw_question

	def parse_sparql(self, raw_query):
		uris = [Uri(raw_uri, DBpedia.parse_uri) for raw_uri in re.findall('<[^>]*>', raw_query)]

		return raw_query, True, uris

	def parse_answers(self, raw_answers):
		if raw_answers is None:
			return []
		answers_set = []
		if "boolean" in raw_answers:
			return [[Answer("bool", raw_answers["boolean"], lambda at, ra: (at, ra))]]
		if "results" in raw_answers and "bindings" in raw_answers["results"] and len(raw_answers["results"]["bindings"]) > 0:
			for raw_ans in raw_answers["results"]["bindings"]:
				answers = []
				for var_id in raw_ans:
					answers.append(Answer(raw_ans[var_id]["type"], raw_ans[var_id]["value"], self.parse_answer))
				answers_set.append(answers)

		return answers_set

	def parse_answer(self, answer_type, raw_answer):
		return answer_type, Uri(raw_answer, DBpedia.parse_uri)

