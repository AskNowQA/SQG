class AnswerRow:
    def __init__(self, raw_answers, parser):
        self.raw_answers = raw_answers
        self.answers = parser(raw_answers)

    def number_of_answer(self):
        return len(self.answers)

    def __eq__(self, other):
        if isinstance(other, AnswerRow):
            if len(self.answers) != len(other.answers):
                return False
            for answer in self.answers:
                found = False
                for other_answer in other.answers:
                    if answer == other_answer:
                        found = True
                if not found:
                    return False
            return True
        return NotImplemented
