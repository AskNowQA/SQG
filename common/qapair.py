from question import Question
from answerset import AnswerSet
from sparql import SPARQL

class QApair:
	def __init__(self, raw_question, raw_answers, raw_query, raw_row, parser):
		self.raw_row = raw_row
		self.question = []
		self.answers = []
		self.sparql = []
		
		self.question = Question(raw_question, parser.parse_question)
		self.answers = AnswerSet(raw_answers, parser.parse_answers)
		self.sparql = SPARQL(raw_query, parser.parse_sparql)

	def question_template(self, entity_relation_list):
		question = self.question.text.lower()
		for item in entity_relation_list:
			question = question.replace(item.label.lower(), item.uri.type)

		return question


	def __str__(self):		
		return "{}\n{}\n{}".format(self.question, self.answers, self.sparql)