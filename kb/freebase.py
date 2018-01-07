from kb import KB
import re
from itertools import chain


class Freebase(KB):
	# http://drogon:9890/sparql
	def __init__(self, endpoint="http://131.220.153.66:9890/sparql"):
		super(Freebase, self).__init__(endpoint)
		self.type_uri = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

	def query_where(self, clauses, return_vars="*", count=False, ask=False):
		if not (count or ask) and return_vars != "*":
			entities = list(chain.from_iterable([re.findall('ns:m.[a-z0-9]*', item) for item in clauses]))
			return super(Freebase, self).query_where(
				[u"FILTER ({} != {})".format(return_vars, entity) for entity in entities] + clauses,
				return_vars=return_vars, count=count, ask=ask)
		return super(Freebase, self).query_where(clauses, return_vars=return_vars, count=count, ask=ask)

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
		elif raw_uri.startswith("?"):
			return "g", raw_uri
		else:
			return raw_uri, raw_uri
