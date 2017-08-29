from node import Node
from edge import Edge


class Path:
    def __init__(self, source_node, edge, dest_node):
        self.source_node = source_node
        self.edge = edge
        self.dest_node = dest_node

    def __str__(self):
        return u"{} --> {} --> {}".format(self.source_node.__str__(), self.edge.__str__(), self.dest_node.__str__()).encode("ascii", "ignore")

    @staticmethod
    def create_path(source_uri, edge_uri, dest_uri):
        source_node = Node(source_uri)
        dest_node = Node(dest_uri)
        edge = Edge(source_node, edge_uri, dest_node)
        return Path(source_node, edge, dest_node)