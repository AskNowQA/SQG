from common.uri import Uri


class Node:
    def __init__(self, uris, mergable=False):
        if isinstance(uris, Uri):
            self.uris = set([uris])
        elif isinstance(uris, list):
            self.uris = set()
            for uri in uris:
                if isinstance(uri, Uri):
                    self.uris.add(uri)
                elif isinstance(uris, list):
                    self.uris.update(uri)
        self.mergable = mergable
        self.inbound = []
        self.outbound = []

    def is_disconnected(self):
        return len(self.inbound) == 0 and len(self.outbound) == 0

    def add_outbound(self, edge):
        if edge not in self.outbound:
            self.outbound.append(edge)

    def remove_outbound(self, edge):
        self.outbound.remove(edge)

    def add_inbound(self, edge):
        if edge not in self.inbound:
            self.inbound.append(edge)

    def remove_inbound(self, edge):
        self.inbound.remove(edge)

    def first_uri_if_only(self):
        if len(self.uris) == 1:
            return next(iter(self.uris))
        return None

    def __are_all_uris_of_type(self, uri_type):
        uris_type = set([u.uri_type for u in self.uris])
        return len(uris_type) == 1 and uris_type.pop() == uri_type

    def are_all_uris_generic(self):
        return self.__are_all_uris_of_type("g")

    def are_all_uris_type(self):
        return self.__are_all_uris_of_type("?t")

    def replace_uri(self, uri, new_uri):
        if uri in self.uris:
            self.uris.remove(uri)
            self.uris.add(new_uri)
            return True
        return False

    def has_uri(self, uri):
        return uri in self.uris

    def sparql_format(self, kb):
        if len(self.uris) == 1:
            return self.first_uri_if_only().sparql_format(kb)
        raise Exception("...")

    def generic_equal(self, other):
        return (self.are_all_uris_generic() and other.are_all_uris_generic()) or self == other

    # def __le__(self, other):
    #     if isinstance(other, Node):
    #         for uri in self.uris:
    #             if not other.has_uri(uri):
    #                 return False
    #
    #         return True
    #     return NotImplemented
    #
    # def __ge__(self, other):
    #     if isinstance(other, Node):
    #         for uri in self.uris:
    #             if not other.has_uri(uri):
    #                 return False
    #
    #         return True
    #     return NotImplemented

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.uris == other.uris
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __str__(self):
        return "\n".join([uri.__str__() for uri in self.uris])
