from node import Node
from edge import Edge
from common.uri import Uri

class Graph:
    def __init__(self, kb):
        self.kb = kb
        self.nodes, self.edges = set(), set()
        self.entity_uris, self.relation_uris, self.answer_uris = set(), set(), set()

    def create_or_get_node(self, uris, mergable=False):
        if isinstance(uris, (int, long)):
            uris = self.__get_generic_uri(0, 0)
            mergable = True
        new_node = Node(uris, mergable)
        for node in self.nodes:
            if node == new_node:
                return node
        return new_node

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def add_edge(self, edge):
        if edge not in self.edges:
            self.add_node(edge.source_node)
            self.add_node(edge.dest_node)
            self.edges.add(edge)

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
                        uri = int(item["callret-1"]["value"])
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
                        elif m == 4:
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
        output = []
        paths = self.__find_paths(self.entity_uris, self.relation_uris, self.edges, [])

        to_be_removed = set()
        for i in range(len(paths)):
            batch_edges = paths[i]
            found_entities = set()
            for edge in batch_edges:
                for uri in self.entity_uris:
                    if edge.has_uri(uri):
                        found_entities.add(uri)
            if len(found_entities) != len(self.entity_uris):
                to_be_removed.add(i)
        to_be_removed = list(to_be_removed)
        to_be_removed.sort(reverse=True)
        for i in to_be_removed:
            paths.pop(i)

        if len(paths) == 1:
            return [[edge.sparql_format() for edge in batch_edges]]

        for batch_edges in paths:
            sparql_where = [edge.sparql_format() for edge in batch_edges]
            result = self.kb.query_where(sparql_where, count=True)
            result = int(result["results"]["bindings"][0]["callret-0"]["value"])
            if result > 0:
                output.append(sparql_where)
        return output

    def __find_paths(self, entity_uris, relation_uris, edges, output=[]):
        new_output = []

        if len(relation_uris) == 0:
            if len(entity_uris) > 0:
                return self.__find_paths(entity_uris, self.relation_uris, edges, output)
            return output

        for relation in relation_uris:
            for edge in self.__find_edges(edges, relation):
                entities = set()
                if not edge.source_node.are_all_uris_generic():
                    entities.update(edge.source_node.uris)
                if not edge.dest_node.are_all_uris_generic():
                    entities.update(edge.dest_node.uris)

                if entities <= entity_uris:
                    valid_edges = self.__find_paths(entity_uris - entities, relation_uris - {relation},
                                                          edges - {edge},
                                                          self.__extend_output(edge, output))
                    if len(valid_edges) > 0 and isinstance(valid_edges[0], list):
                        valid_edges = valid_edges[0]
                    new_output.append(valid_edges)

        return new_output

    def __extend_output(self, edge, output):
        new_output = []
        if len(output) == 0:
            output.append([])
        for item in output:
                new_output.append(item + [edge])
        return new_output

    def __find_edges(self, edges, uri):
        return [edge for edge in edges if edge.uri == uri]

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
        to_be_removed = set()
        for edge_1 in self.edges:
            for edge_2 in self.edges:
                if edge_1 == edge_2 or edge_2 in to_be_removed:
                    continue
                if edge_1.generic_equal(edge_2):
                    to_be_removed.append(edge_2)
        for item in to_be_removed:
            self.remove_edge(item)

    def __str__(self):
        return "\n".join([edge.full_path() for edge in self.edges])
