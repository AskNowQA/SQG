class Answer:
	def __init__(self, answer_type, raw_answer, parser):
		self.raw_answer = raw_answer
		self.type, self.text = parser(answer_type, raw_answer)

	def __str__(self):
		return self.text.encode("ascii","ignore")