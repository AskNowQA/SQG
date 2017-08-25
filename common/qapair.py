from question import Question
from answers import Answers
from sparql import SPARQL

class QApair:
	def __init__(self, raw_question, raw_answers, raw_query, parser):
		self.question = []
		self.answers = []
		self.sparql = []
		
		self.question = Question(raw_question, parser.parse_question)
		self.answers = Answers(raw_answers, parser.parse_answers)
		self.sparql = SPARQL(raw_query, parser.parse_sparql)

	def __str__(self):		
		return "{}\n{}\n{}".format(self.question, self.answers, self.sparql)