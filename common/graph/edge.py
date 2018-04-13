class Edge:
    def __init__(self, source_node, uri, dest_node):
        self.source_node = source_node
        self.uri = uri
        self.dest_node = dest_node
        self.source_node.add_outbound(self)
        self.dest_node.add_inbound(self)
        self.__confidence = (
                                self.source_node.confidence if self.source_node is not None else 1) * self.uri.confidence * (
                                self.dest_node.confidence if self.dest_node is not None else 1)
        self.__hash = ("" if source_node is None else self.source_node.__str__()) + self.uri.__str__() + (
            "" if dest_node is None else self.dest_node.__str__())

    @property
    def confidence(self):
        return self.__confidence

    def copy(self, source_node=None, uri=None, dest_node=None):
        return Edge(self.source_node if source_node is None else source_node,
                    self.uri if uri is None else uri,
                    self.dest_node if dest_node is None else dest_node)

    def has_uri(self, uri):
        return self.uri == uri or self.source_node.has_uri(uri) or self.dest_node.has_uri(uri)

    def prepare_remove(self):
        self.source_node.remove_outbound(self)
        self.dest_node.remove_inbound(self)

    def max_generic_id(self):
        s = self.source_node.first_uri_if_only()
        if s is not None:
            s = s.generic_id()
        if s is None:
            s = -1

        d = self.dest_node.first_uri_if_only()
        if d is not None:
            d = d.generic_id()
        if d is None:
            d = -1

        return max(s, d)

    def sparql_format(self, kb):
        return u"{} {} {}".format(self.source_node.sparql_format(kb), self.uri.sparql_format(kb),
                                  self.dest_node.sparql_format(kb))

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
            if hasattr(self, "__hash"):
                return self.__hash == other.__hash
            else:
                return self.source_node == other.source_node and self.uri == other.uri and self.dest_node == other.dest_node

        return NotImplemented

    def __str__(self):
        return self.uri.__str__()
