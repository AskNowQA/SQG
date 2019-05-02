class Uri:
    def __init__(self, raw_uri, parser, confidence=1.0):
        self.raw_uri = raw_uri
        self.uri_type, self.uri = parser(raw_uri)
        self.__str = u"{}:{}".format(self.uri_type, self.uri[self.uri.rfind("/") + 1:].encode("ascii", "ignore").decode())
        self.__hash = hash(self.__str)
        self.confidence = confidence

    def is_generic(self):
        return self.uri_type == "g"

    def is_entity(self):
        return self.uri_type == "?s"

    def is_ontology(self):
        return self.uri_type == "?p" or self.uri_type == "?o"

    def is_type(self):
        return self.uri_type == "?t"

    def sparql_format(self, kb):
        return kb.uri_to_sparql(self)

    def generic_id(self):
        if self.is_generic():
            return int(self.uri[3:])
        return None

    def generic_equal(self, other):
        return (self.is_generic() and other.is_generic()) or self == other

    def __eq__(self, other):
        if isinstance(other, Uri):
            return self.uri == other.uri
        return NotImplemented

    def __hash__(self):
        return self.__hash

    def __str__(self):
        return self.__str

    @staticmethod
    def generic_uri(var_num):
        return Uri("g", lambda r: ("g", "?u_{}".format(var_num)))
