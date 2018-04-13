from common.container.uri import Uri
import numpy as np


class Node:
    def __init__(self, uris, mergable=False):
        if isinstance(uris, Uri):
            self.__uris = set([uris])
        elif isinstance(uris, list):
            self.__uris = set()
            for uri in uris:
                if isinstance(uri, Uri):
                    self.__uris.add(uri)
                elif isinstance(uris, list):
                    self.__uris.update(uri)
        self.uris_hash = self.__str__()
        self.mergable = mergable
        self.inbound = []
        self.outbound = []
        self.__confidence = np.prod([uri.confidence for uri in self.__uris])

    @property
    def confidence(self):
        return self.__confidence

    @property
    def uris(self):
        return self.__uris

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
        if len(self.__uris) == 1:
            return next(iter(self.__uris))
        return None

    def __are_all_uris_of_type(self, uri_type):
        uris_type = set([u.uri_type for u in self.__uris])
        return len(uris_type) == 1 and uris_type.pop() == uri_type

    def are_all_uris_generic(self):
        return self.__are_all_uris_of_type("g")

    def are_all_uris_type(self):
        return self.__are_all_uris_of_type("?t")

    def replace_uri(self, uri, new_uri):
        if uri in self.__uris:
            self.__uris.remove(uri)
            self.__uris.add(new_uri)
            return True
        return False

    def has_uri(self, uri):
        return uri in self.__uris

    def sparql_format(self, kb):
        if len(self.__uris) == 1:
            return self.first_uri_if_only().sparql_format(kb)
        raise Exception("...")

    def generic_equal(self, other):
        return (self.are_all_uris_generic() and other.are_all_uris_generic()) or self == other

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Node):
            # return self.__uris == other.__uris
            return self.uris_hash == other.uris_hash
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __str__(self):
        return "\n".join(sorted([uri.__str__() for uri in self.__uris]))
