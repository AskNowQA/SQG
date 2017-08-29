class Uri:
	def __init__(self, raw_uri, parser):
		self.raw_uri = raw_uri
		self.type, self.uri = parser(raw_uri) 

	def is_entity(self):
		return self.type == "?s"

	def is_ontology(self):
		return self.type == "?p"

	def sparql_format(self):
		return u"<{}>".format(self.uri)

	def __str__(self):
		return self.uri.encode("ascii", "ignore")
