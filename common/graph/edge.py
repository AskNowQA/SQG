class Edge:
    def __init__(self, source_node, uri, dest_node):
        self.source_node = source_node
        self.uri = uri
        self.dest_node = dest_node

    def sparql_format(self):
        return self.uri.sparql_format()

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.uri == other.uri
        return NotImplemented

    def __str__(self):
        return self.uri.__str__()
