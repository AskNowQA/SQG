from kb import KB


class DBpedia(KB):
	# http://kb.org/sparql
	# http://drogon:7890/sparql
	def __init__(self, endpoint="http://drogon:7890/sparql"):
		super(DBpedia, self).__init__(endpoint)
		self.type_uri = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

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

	@staticmethod
	def uri_to_sparql(input_uri):
		if input_uri.uri_type == "g":
			return input_uri.uri
		return u"<{}>".format(input_uri.uri)
