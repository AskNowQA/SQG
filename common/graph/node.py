class Node:
    def __init__(self, uri):
        self.uri = uri
        self.inbound = []
        self.outbound = []

    def __str__(self):
        return self.uri.sparql_format().encode("ascii", "ignore")
