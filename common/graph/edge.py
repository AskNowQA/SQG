class Edge:
    def __init__(self, source_node, uri, dest_node):
        self.source_node = source_node
        self.uri = uri
        self.dest_node = dest_node
        self.source_node.add_outbound(self)
        self.dest_node.add_inbound(self)

    def prepare_remove(self):
        self.source_node.remove_outbound(self)
        self.dest_node.remove_inbound(self)

    def sparql_format(self):
        return u"{} {} {}".format(self.source_node.sparql_format(), self.uri.sparql_format(), self.dest_node.sparql_format())

    def full_path(self):
        return "{} --> {} --> {}".format(self.source_node.__str__(), self.uri.__str__(), self.dest_node.__str__())

    def generic_equal(self, other):
        if isinstance(other, Edge):
            return self.source_node.generic_equal(other.source_node) \
                and self.dest_node.generic_equal(other.dest_node) \
                and self.uri.generic_equal(other.uri)
        return NotImplemented

    def __hash__(self):
        return hash(self.full_path())

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.source_node == other.source_node and self.uri == other.uri and self.dest_node == other.dest_node
        return NotImplemented

    def __str__(self):
        return self.uri.__str__()
