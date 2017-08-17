import json
from qapair import QApair
from answer import Answer

class WebQSP:
	def __init__(self, path = "/home/hamid/workspace/query_generation/data/WebQuestionsSP/WebQSP.train.json"):
		self.raw_data = []
		self.qapairs = []
		self.path = path

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):
		parser = QaldParser()
		for raw_row in self.raw_data["Questions"]:
			self.qapairs.append(QApair(raw_row["ProcessedQuestion"], raw_row["Parses"], raw_row["Parses"], parser))

	def print_pairs(self, n = -1):
		for item in self.qapairs[0:n]:
			print item
			print ""

class QaldParser:
	def parse_question(self, raw_question):
		return raw_question

	def parse_sparql(self, raw_query):
		# if len(raw_query)>1:
		# 	print raw_query
		return raw_query[0]["Sparql"] if "Sparql" in raw_query[0] else ""

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

