import json
from qapair import QApair
from answer import Answer

class LC_Qaud:	
	def __init__(self, path = "/home/hamid/workspace/query_generation/data/LC-QUAD/data_v8.json"):
		self.raw_data = []
		self.qapairs = []
		self.path = path

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):
		parser = LC_QaudParser()
		for raw_row in self.raw_data:
			self.qapairs.append(QApair(raw_row["corrected_question"], "", raw_row["sparql_query"], parser))

	def print_pairs(self, n = -1):
		for item in self.qapairs[0:n]:
			print item
			print ""


class LC_QaudParser:
	def parse_question(self, raw_question):
		return raw_question

	def parse_sparql(self, raw_query):
		return raw_query

	def parse_answers(self, raw_answers):		
			return []

	def parse_answer(self, answer_type, raw_answer):
		return "",""
