from common.uri import Uri


class Node:
    def __init__(self, uris, mergable=False):
        if isinstance(uris, Uri):
            self.uris = [uris]
        elif isinstance(uris, list):
            self.uris = []
            for uri in uris:
                if isinstance(uri, Uri):
                    self.uris.append(uri)
                elif isinstance(uris, list):
                    self.uris.extend(uri)
        self.uris = list(set(self.uris))
        self.mergable = mergable
        self.inbound = []
        self.outbound = []

    def __all_generic_uris(self):
        uris_type = set([u.uri_type for u in self.uris])
        return len(uris_type) == 1 and uris_type.pop() == "g"

    def replace_uri(self, uri, new_uri):
        for i in range(len(self.uris)):
            if self.uris[i] == uri:
                self.uris[i] = new_uri
                if self.__all_generic_uris():
                    self.uris = [new_uri]
                return True
        return False

    def has_uri(self, uri):
        for u in self.uris:
            if u == uri:
                return True
        return False

    def sparql_format(self):
        if len(self.uris) == 1:
            return self.uris[0].sparql_format()
        raise Exception("...")

    def __eq__(self, other):
        if isinstance(other, Node):
            for uri in self.uris:
                if not other.has_uri(uri):
                    return False

            return True
        return NotImplemented

    def __str__(self):
        output = []
        for uri in self.uris:
            output.append(uri.__str__())
        return output
