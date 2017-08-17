from answer import Answer

class Answers:
	def __init__(self, raw_answers, parser):
		self.raw_answers = raw_answers
		self.answers = []		
		self.answers = parser(raw_answers)
		if self.answers is None:
			print raw_answers
			print self.answers
			print parser(raw_answers)
			q = 1/0 

	def __str__(self):
		try:
			return "\n".join(str(a) for a in self.answers)
		except Exception as e:
			print self.raw_answers
			print self.answers
			raise e
		