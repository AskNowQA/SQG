class AnswerSet:
	def __init__(self, raw_answerset, parser):
		self.raw_answerset = raw_answerset
		self.answer_rows = []
		self.answer_rows = parser(raw_answerset)

	def __eq__(self, other):
		if isinstance(other, AnswerSet):
			if len(self.answer_rows) != len(other.answer_rows):
				return False
			for answers in self.answer_rows:
				found = False
				for other_answers in other.answer_rows:
					if answers == other_answers:
						found = True
				if not found:
					return False
			return True
		return NotImplemented

	def __len__(self):
		return len(self.answer_rows)

	def __str__(self):
		return "\n".join(str(a) for a in self.answers)
