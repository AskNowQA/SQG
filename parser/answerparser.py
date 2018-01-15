from common.container.answer import Answer
from common.container.answerrow import AnswerRow
from common.container.uri import Uri


class AnswerParser(object):
    def __init__(self, kb):
        self.kb = kb

    def parse_queryresult(self, raw_answerset):
        answer_rows = []
        if raw_answerset is None:
            return answer_rows
        if "boolean" in raw_answerset:
            return [
                AnswerRow(raw_answerset, lambda x: [Answer("bool", raw_answerset["boolean"], lambda at, ra: (at, ra))])]
        if "results" in raw_answerset and "bindings" in raw_answerset["results"] \
                and len(raw_answerset["results"]["bindings"]) > 0:
            for raw_answerrow in raw_answerset["results"]["bindings"]:
                answer_rows.append(AnswerRow(raw_answerrow, self.__parse_answerrow))
        elif "string" in raw_answerset:
            return [
                AnswerRow(raw_answerset, lambda x: [Answer("uri", raw_answerset["string"], self.__parse_answer)])]


        return answer_rows

    def __parse_answerrow(self, raw_answerrow):
        answers = []
        for var_id in raw_answerrow:
            answers.append(Answer(raw_answerrow[var_id]["type"], raw_answerrow[var_id]["value"], self.__parse_answer))
        return answers

    def __parse_answer(self, answer_type, raw_answer):
        prefix = self.kb.prefix()
        if len(prefix) > 0 and raw_answer.startswith(prefix):
            raw_answer = self.kb.shorten_prefix() + raw_answer[len(prefix):]
        return answer_type, Uri(raw_answer, self.kb.parse_uri)
