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
    def create_path(uris):
        if len(uris) == 3:
            source_node = Node(uris[0])
            dest_node = Node(uris[2])
            edge = Edge(source_node, uris[1], dest_node)
            return Path(source_node, edge, dest_node)
        else:
            source_node = Node(uris[0])
            dest_node = Path.create_path(uris[2:])
            edge = Edge(source_node, uris[1], dest_node)
            return Path(source_node, edge, dest_node)
