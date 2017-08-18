class SPARQL:
	def __init__(self, raw_query, parser):
		self.raw_query = raw_query
		self.query, self.supported, self.uris = parser(raw_query)

	def __str__(self):
		return self.query.encode("ascii","ignore")