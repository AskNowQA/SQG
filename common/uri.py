class Uri:
	def __init__(self, raw_uri, parser):
		self.raw_uri = raw_uri
		self.type, self.uri = parser(raw_uri) 

	def __str__(self):
		return self.raw_uri.encode("ascii","ignore")
		