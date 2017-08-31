class Answer:
	def __init__(self, answer_type, raw_answer, parser):
		self.raw_answer = raw_answer
		self.answer_type, self.answer = parser(answer_type, raw_answer)

	def __str__(self):
		if self.answer_type == "bool":
			return str(self.answer)
		elif self.answer_type == "uri":
			return self.answer.__str__().encode("ascii", "ignore")

		return self.answer.encode("ascii", "ignore")
