from kb import KB
from common.graph.path import Path
from common.uri import Uri


class Freebase(KB):
	# http://drogon:9890/sparql
	def __init__(self, endpoint="http://drogon:9890/sparql"):
		super(Freebase, self).__init__(endpoint)
		self.type_uri = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

	def get_answers_type(self, answer_set):
		where = ""
		for answer_row in answer_set.answer_rows:
			for answer in answer_row.answers:
				where += u"{} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?u .".format(answer.answer.sparql_format())
		return self.query(u"SELECT * WHERE {{ {} }}".format(where))

	@staticmethod
	def parse_uri(input_uri):
		if isinstance(input_uri, bool):
			return "bool", input_uri
		raw_uri = input_uri.strip("<>")
		if raw_uri.find("/resource/") >= 0:
			return "?s", raw_uri
		elif raw_uri.find("/ontology/") >= 0 or raw_uri.find("/property/") >= 0:
			return "?p", raw_uri
		elif raw_uri.find("rdf-syntax-ns#type") >= 0:
			return "?t", raw_uri
		else:
			return "?u", raw_uri
