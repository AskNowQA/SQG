import itertools
from common.linkeditem import LinkedItem
from common.uri import Uri

class Jerrl:
	def __init__(self):
		pass

	def do(self, qapair):
		return [u for u in qapair.sparql.uris if u.is_entity()], \
			   [u for u in qapair.sparql.uris if u.is_ontology()]
