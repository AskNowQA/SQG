from node import Node
from edge import Edge
from common.uri import Uri

class Graph:
    def __init__(self, kb):
        self.kb = kb
        self.nodes, self.edges = [], []
        self.entity_uris, self.relation_uris, self.answer_uris = set(), set(), set()

    def create_or_get_node(self, uris, mergable=False):
        node = Node(uris, mergable)
        return self.nodes[self.nodes.index(node)] if node in self.nodes else node

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def add_edge(self, edge):
        if edge not in self.edges:
            self.add_node(edge.source_node)
            self.add_node(edge.dest_node)
            self.edges.append(edge)

    def remove_edge(self, edge):
        edge.prepare_remove()
        self.edges.remove(edge)
        if edge.source_node.is_disconnected():
            self.remove_node(edge.source_node)
        if edge.dest_node.is_disconnected():
            self.remove_node(edge.dest_node)

    def __one_hop_graph(self, entity_uris, relation_uris):
        for entity_uri in entity_uris:
            for relation_uri in relation_uris:
                result = self.kb.one_hop_graph(entity_uri.sparql_format(), relation_uri.sparql_format())
                if result is not None:
                    for item in result:
                        m = int(item["m"]["value"])
                        uri = Uri(item["u1"]["value"], self.kb.parse_uri)
                        if m == 0:
                            n_s = self.create_or_get_node(uri, True)
                            n_d = self.create_or_get_node(entity_uri)
                            e = Edge(n_s, relation_uri, n_d)
                            self.add_edge(e)
                        elif m == 1:
                            n_d = self.create_or_get_node(uri, True)
                            n_s = self.create_or_get_node(entity_uri)
                            e = Edge(n_s, relation_uri, n_d)
                            self.add_edge(e)
                        elif m == 2:
                            n_d = self.create_or_get_node(relation_uri)
                            n_s = self.create_or_get_node(entity_uri)
                            e = Edge(n_s, uri, n_d)
                            self.add_edge(e)
                        elif m == 3:
                            n_d = self.create_or_get_node(entity_uri)
                            n_s = self.create_or_get_node(relation_uri)
                            e = Edge(n_s, uri, n_d)
                            self.add_edge(e)

    def find_minimal_subgraph(self, entity_uris, relation_uris, answer_uris):
        self.entity_uris, self.relation_uris, self.answer_uris = entity_uris, relation_uris, answer_uris

        self.__one_hop_graph(entity_uris, relation_uris)

        if len(self.edges) > 100:
            return
        for edge in self.edges:
            mergable_node = None
            entity_node = None
            if edge.source_node.mergable:
                mergable_node = edge.source_node
            if edge.dest_node.mergable:
                mergable_node = edge.dest_node
            if not edge.source_node.mergable:
                entity_node = edge.source_node
            if not edge.dest_node.mergable:
                entity_node = edge.dest_node
            if mergable_node is not None and entity_node is not None:
                self.__one_hop_graph(entity_uris - set(entity_node.uris),
                        relation_uris - set([e.uri for e in entity_node.inbound + entity_node.outbound]))

    def to_where_statement(self):
        self.__generalize_nodes()
        self.__merge_edges()
        return [edge.sparql_format() for edge in self.edges]

    def __get_generic_uri(self, uri, edges):
        return Uri.generic_uri(0)

    def __generalize_nodes(self):
        uris = self.entity_uris.union(self.relation_uris)
        for node in self.nodes:
            for uri in node.uris:
                if uri not in uris:
                    generic_uri = self.__get_generic_uri(uri, node.inbound + node.outbound)
                    node.replace_uri(uri, generic_uri)

    def __merge_edges(self):
        # Merge edges
        i = 0
        while i < len(self.edges):
            to_be_removed = []
            for j in range(i, len(self.edges)):
                if i == j:
                    continue
                if self.edges[j] not in to_be_removed and self.edges[i].generic_equal(self.edges[j]):
                    to_be_removed.append(self.edges[j])
            for item in to_be_removed:
                self.remove_edge(item)
            i += 1

    def __str__(self):
        return "\n".join([edge.full_path() for edge in self.edges])


