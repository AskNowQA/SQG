class Edge:
    def __init__(self, source_node, uri, dest_node):
        self.source_node = source_node
        self.uri = uri
        self.dest_node = dest_node

    def __str__(self):
        return self.uri.sparql_format().encode("ascii", "ignore")
