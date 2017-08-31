class Uri:
	def __init__(self, raw_uri, parser):
		self.raw_uri = raw_uri
		self.uri_type, self.uri = parser(raw_uri)

	def __eq__(self, other):
		if isinstance(other, Uri):
			return self.uri_type == other.uri_type and self.uri == other.uri
		return NotImplemented

	def is_entity(self):
		return self.uri_type == "?s"

	def is_ontology(self):
		return self.uri_type == "?p"

	def sparql_format(self):
		if self.uri_type == "g":
			return self.uri
		return u"<{}>".format(self.uri)

	def __str__(self):
		return "{}:{}".format(self.uri_type, self.uri[self.uri.rfind("/") + 1:].encode("ascii", "ignore"))

	@staticmethod
	def generic_uri(var_num):
		return Uri("g", lambda r: ("g", "?u_{}".format(var_num)))
