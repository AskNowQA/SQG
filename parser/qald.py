import json, re
from common.qapair import QApair
from common.uri import Uri
from common.answerrow import AnswerRow
from common.answer import Answer
from kb.dbpedia import DBpedia
from answerparser import AnswerParser

class Qald:
	qald_5 = "./data/QALD/5/data/qald-5_train.json"
	qald_6 = "./data/QALD/6/data/qald-6-train-multilingual.json"
	qald_7_largescale = "./data/QALD/7/data/qald-7-train-largescale.json"
	qald_7_multilingual = "./data/QALD/7/data/qald-7-train-multilingual.json"
	qald_8 = "./data/QALD/8/data/wikidata-train-7.json"

	def __init__(self, path):
		self.raw_data = []
		self.qapairs = []
		self.path = path
		self.parser = QaldParser()

	def load(self):
		with open(self.path) as data_file:	
			self.raw_data = json.load(data_file)

	def parse(self):
		parser = QaldParser()
		for raw_row in self.raw_data["questions"]:
			question = ""
			query = ""
			if "question" in raw_row:
				question = raw_row["question"]
			elif "body" in raw_row:
				# QALD-5 format
				question = raw_row["body"]
			if "query" in raw_row:
				query = raw_row["query"]
			self.qapairs.append(QApair(question, raw_row["answers"], query, raw_row, raw_row["id"], parser))

	def print_pairs(self, n=-1):
		for item in self.qapairs[0:n]:
			print item
			print ""


class QaldParser(AnswerParser):
	def __init__(self):
		super(QaldParser, self).__init__(DBpedia())


	def parse_question(self, raw_question):
		for q in raw_question:
			if q["language"] == "en":
				return q["string"]

	def parse_sparql(self, raw_query):
		if "sparql" in raw_query:
			raw_query = raw_query["sparql"]
		elif isinstance(raw_query, basestring) and "where" in raw_query.lower():
			pass
		else:
			raw_query = ""
		if "PREFIX " in raw_query:
			#QALD-5 bug!
			raw_query = raw_query.replace("htp:/w.", "http://www.")
			raw_query = raw_query.replace("htp:/dbpedia.", "http://dbpedia.")

			for item in re.findall("PREFIX [^:]*: <[^>]*>", raw_query):
				prefix = item[7:item.find(" ", 9)]
				uri = item[item.find("<"):-1]
				raw_query = raw_query.replace(prefix, uri)
			idx = raw_query.find("WHERE")
			idx2 = raw_query[:idx - 1].rfind(">")
			raw_query = raw_query[idx2 + 1:]
			for uri in re.findall('<[^ ]*', raw_query):
				raw_query = raw_query.replace(uri, uri + ">")

		uris = [Uri(raw_uri, self.kb.parse_uri) for raw_uri in re.findall('<[^>]*>', raw_query)]
		supported = not any(substring in raw_query for substring in ["UNION", "FILTER", "OFFSET", "HAVING", "LIMIT"])
		return raw_query, supported, uris

	def parse_answerset(self, raw_answers):
		if len(raw_answers) == 0:
			return []
		elif len(raw_answers) == 1:
			return self.parse_queryresult(raw_answers[0])
		else:
			result = []
			for item in raw_answers:
				result.append(
					AnswerRow(item["string"],
							  lambda x: [Answer("uri", x, lambda t, y: ("uri", Uri(y, self.kb.parse_uri)))]))



			return result

	def parse_answerrow(self, raw_answerrow):
		answers = [Answer(raw_answerrow["AnswerType"], raw_answerrow, self.parse_answer)]
		return answers

	def parse_answer(self, answer_type, raw_answer):
		if answer_type == "boolean":
			return answer_type, str(raw_answer)
		else:
			if not answer_type in raw_answer:
				answer_type = "\"{}\"".format(answer_type)
			return raw_answer[answer_type]["type"], Uri(raw_answer[answer_type]["value"], self.kb.parse_uri)
