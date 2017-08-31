
class Node:
    def __init__(self, uri):
        self.uri = uri
        self.inbound = []
        self.outbound = []

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.uri == other.uri
        return NotImplemented

    def __str__(self):
        return self.uri.__str__()
