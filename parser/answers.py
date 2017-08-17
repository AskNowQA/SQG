from answer import Answer

class Answers:
	def __init__(self, raw_answers, parser):
		self.raw_answers = raw_answers
		self.answers = []
		self.answers = parser(raw_answers)

	def __str__(self):
		return "\n".join(str(a) for a in self.answers)