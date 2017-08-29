import json, re
from common.qapair import QApair
from common.answer import Answer
from common.uri import Uri

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
		uris = [Uri(raw_uri, self.parse_uri) for raw_uri in re.findall('<[^>]*>',raw_query)]

		return raw_query, True, uris

	def parse_answers(self, raw_answers):
		if raw_answers is None:
			return []
		answers = []
		if "boolean" in raw_answers:
			return [Answer("boolean", raw_answers["boolean"], self.parse_answer)]
		if "results" in raw_answers and "bindings" in raw_answers["results"] and len(raw_answers["results"]["bindings"]) > 0:
			for raw_ans in raw_answers["results"]["bindings"]:
				for var_id in raw_ans:
					answers.append(Answer(raw_ans[var_id]["type"], raw_ans[var_id]["value"], self.parse_answer))

		return answers

	def parse_answer(self, answer_type, raw_answer):
		return answer_type, raw_answer

	def parse_uri(self, raw_uri):
		if raw_uri.find("/resource/") >= 0:
			return "?s", raw_uri
		elif raw_uri.find("/ontology/") >= 0 or raw_uri.find("/property/") >= 0:
			return "?p", raw_uri
		elif raw_uri.find("rdf-syntax-ns#type") >= 0:
			return "?t", raw_uri
		else:
			return "?u", raw_uri