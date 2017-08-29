class SPARQL:
	def __init__(self, raw_query, parser):
		self.raw_query = raw_query
		self.query, self.supported, self.uris = parser(raw_query)
		self.extrat_where_template()

	def extrat_where_template(self):
		WHERE = "WHERE"
		sparql_query = self.query.strip(" {};\t")
		for uri in self.uris:
			sparql_query = sparql_query.replace(uri.uri, uri.type)

		idx = sparql_query.find(WHERE)
		self.where_clause = ' '.join(sparql_query.split())
		if idx >= 0:
			 self.where_clause= ' '.join(self.where_clause[idx +len(WHERE) + 1:].strip("{}. ").replace(".", " ").split())


	def __str__(self):
		return self.query.encode("ascii","ignore")