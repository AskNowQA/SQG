from kb import KB


class Freebase(KB):
	# http://drogon:9890/sparql
	def __init__(self, endpoint="http://drogon:9890/sparql"):
		super(Freebase, self).__init__(endpoint)
		self.type_uri = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

	@staticmethod
	def shorten_prefix():
		return "ns:"

	@staticmethod
	def prefix():
		return "http://rdf.freebase.com/ns/"

	@staticmethod
	def query_prefix():
		return "PREFIX {} <{}>".format(Freebase.shorten_prefix(), Freebase.prefix())

	@staticmethod
	def parse_uri(input_uri):
		if isinstance(input_uri, bool):
			return "bool", input_uri
		raw_uri = input_uri.strip("<>")
		if raw_uri.find("ns:m.") >= 0:
			return "?s", raw_uri
		elif raw_uri.find("ns:") >= 0:
			return "?p", raw_uri
		else:
			return raw_uri, raw_uri
