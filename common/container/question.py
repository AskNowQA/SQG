class Question:
	def __init__(self, raw_question, parser):
		self.text = ""
		self.raw_question = raw_question
		self.text = parser(raw_question)

	def __str__(self):
		return self.text.encode("ascii", "ignore")

