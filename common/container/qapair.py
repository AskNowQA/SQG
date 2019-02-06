from common.container.question import Question
from common.container.answerset import AnswerSet
from common.container.sparql import SPARQL

class QApair:
	def __init__(self, raw_question, raw_answerset, raw_query, raw_row, id, parser):
		self.raw_row = raw_row
		self.question = []
		self.sparql = []
		self.id = id
		
		self.question = Question(raw_question, parser.parse_question)
		self.answerset = AnswerSet(raw_answerset, parser.parse_answerset)
		self.sparql = SPARQL(raw_query, parser.parse_sparql)

	def question_template(self, entity_relation_list):
		question = self.question.text.lower()
		for item in entity_relation_list:
			question = question.replace(item.label.lower(), item.uri.type)
		return question

	def __str__(self):
		return "{}\n{}\n{}".format(self.question, self.answerset, self.sparql)
