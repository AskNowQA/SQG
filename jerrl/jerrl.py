import itertools
from common.linkeditem import LinkedItem
from common.uri import Uri

class Jerrl:
	def __init__(self):
		pass

	def do(self, qapair):
		items = []
		for raw_item in itertools.chain(qapair.raw_row["predicate mapping"], qapair.raw_row["entity mapping"]):
			items.append(LinkedItem(raw_item, self.parse_linkeditem))
		return items

	def parse_linkeditem(self, raw_item):
		return Uri(raw_item["uri"], self.parse_uri), raw_item["seq"], raw_item["label"]
	
	def parse_uri(self, raw_uri):
		if raw_uri.find("/resource/") >= 0:
			return "?s", raw_uri
		elif raw_uri.find("/ontology/") >= 0 or raw_uri.find("/property/") >= 0:
			return "?p", raw_uri
		elif raw_uri.find("rdf-syntax-ns#type") >= 0:
			return "?t", raw_uri
		else:
			return "?u", raw_uri
