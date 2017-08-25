class LinkedItem:
	def __init__(self, raw_item, parser):
		self.raw_item = raw_item
		self.uri, self.positions, self.label = parser(raw_item)
		

