import requests
from kb import KB
from common.graph.path import Path
from common.uri import Uri


class DBpedia(KB):
	# http://kb.org/sparql
	# http://drogon:7890/sparql
	def __init__(self, endpoint="http://drogon:7890/sparql"):
		super(DBpedia, self).__init__(endpoint)
		self.type_uri = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

	def __find_minimal_subgraph(self, ent1, ent2, hop=1, direction=0):
		result = []
		if hop == 1:
			ent1_str = ent1.sparql_format()
			ent2_str = ent2.sparql_format()

			if direction == 1:
				ent1_str, ent2_str = ent2_str, ent1_str

			query = u"SELECT * WHERE {{ {} ?uri {} }} LIMIT 100".format(ent1_str, ent2_str)
			status, response = self.query(query)
			if status == 200 and len(response["results"]["bindings"]) > 0:
				result.append(response["results"]["bindings"])
		elif hop == 2:
			if direction == 0:
				query = u"SELECT * WHERE {{ {} ?o1 ?r1. ?r1 ?o2 {} }} LIMIT 100".format(ent1.sparql_format(), ent2.sparql_format())
			else:
				query = u"SELECT * WHERE {{ ?r1 ?o1 {} . ?r1 ?o2 {} }} LIMIT 100".format(ent1.sparql_format(), ent2.sparql_format())

			status, response = self.query(query)
			if status == 200 and len(response["results"]["bindings"]) > 0:
				result.append(response["results"]["bindings"])
		return result

	def find_minimal_subgraph(self, ent1, ent2, is_answer, max_hop=1):
		result = []
		for hop in range(1, max_hop + 1):
			for direction in range(2):
				raw_results = self.__find_minimal_subgraph(ent1, ent2, hop, direction)
				if len(raw_results) > 0:
					for raw_result in raw_results:
						result.extend(self.__convert_to_path(ent1, ent2, hop, direction, raw_result, is_answer))
					return result

	def __convert_to_path(self, ent1, ent2, hop, direction, raw_result, is_answer):
		results = []

		if hop == 1:
			if direction == 1:
				ent1, ent2 = ent2, ent1
			for item in raw_result:
				edge_uri = Uri(item["uri"]["value"], DBpedia.parse_uri)
				results.append(Path.create_path([ent1, edge_uri, ent2], is_answer))
		if hop == 2:
			if direction == 0:
				for item in raw_result:
					o1 = Uri(item["o1"]["value"], DBpedia.parse_uri)
					r1 = Uri(item["r1"]["value"], DBpedia.parse_uri)
					o2 = Uri(item["o2"]["value"], DBpedia.parse_uri)
					results.append(Path.create_path([ent1, o1, r1, o2, ent2], is_answer))
			elif direction == 1:
				for item in raw_result:
					o1 = Uri(item["o1"]["value"], DBpedia.parse_uri)
					r1 = Uri(item["r1"]["value"], DBpedia.parse_uri)
					o2 = Uri(item["o2"]["value"], DBpedia.parse_uri)
					results.append(Path.create_path([r1, o1, ent1], is_answer))
					results.append(Path.create_path([r1, o2, ent2], is_answer))

		return results

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
