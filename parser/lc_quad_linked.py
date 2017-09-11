import json, re
from common.qapair import QApair
from common.answer import Answer
from common.answerrow import AnswerRow
from common.uri import Uri
from kb.dbpedia import DBpedia


class LC_Qaud_Linked:	
	def __init__(self, path="./data/LC-QUAD/linked.json"):
		self.raw_data = []
		self.qapairs = []
		self.path = path
		self.parser = LC_Qaud_LinkedParser()

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):		
		for raw_row in self.raw_data:
			self.qapairs.append(QApair(raw_row["question"], raw_row.get("answers"), raw_row["sparql_query"], raw_row, raw_row["id"], self.parser))

	def print_pairs(self, n=-1):
		for item in self.qapairs[0:n]:
			print item
			print ""


class LC_Qaud_LinkedParser:
	def parse_question(self, raw_question):
		return raw_question

	def parse_sparql(self, raw_query):
		uris = [Uri(raw_uri, DBpedia.parse_uri) for raw_uri in re.findall('<[^>]*>', raw_query)]
		return raw_query, True, uris

	def parse_answerset(self, raw_answerset):
		answer_rows = []
		if raw_answerset is None:
			return answer_rows
		if "boolean" in raw_answerset:
			return [AnswerRow(raw_answerset, lambda x: [Answer("bool", raw_answerset["boolean"], lambda at, ra: (at, ra))])]
		if "results" in raw_answerset and "bindings" in raw_answerset["results"] \
				and len(raw_answerset["results"]["bindings"]) > 0:
			for raw_answerrow in raw_answerset["results"]["bindings"]:
				answer_rows.append(AnswerRow(raw_answerrow, self.parse_answerrow))
		return answer_rows

	def parse_answerrow(self, raw_answerrow):
		answers = []
		for var_id in raw_answerrow:
			answers.append(Answer(raw_answerrow[var_id]["type"], raw_answerrow[var_id]["value"], self.parse_answer))
		return answers

	def parse_answer(self, answer_type, raw_answer):
		return answer_type, Uri(raw_answer, DBpedia.parse_uri)

