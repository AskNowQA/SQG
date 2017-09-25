from node import Node
from edge import Edge
from common.uri import Uri
from common.utility.mylist import MyList
import itertools


class Graph:
    def __init__(self, kb):
        self.kb = kb
        self.nodes, self.edges = set(), set()
        self.entity_uris, self.relation_uris = [], []
        self.suggest_retrieve_id = 0

    def create_or_get_node(self, uris, mergable=False):
        if isinstance(uris, (int, long)):
            uris = self.__get_generic_uri(uris, 0)
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

    def __one_hop_graph(self, entity_uris, relation_uris, number_of_entities=1):
        for relation_uri in relation_uris:
            for entity_uri in itertools.combinations(entity_uris, number_of_entities):
                result = self.kb.one_hop_graph(entity_uri[0], relation_uri, entity_uri[1] if len(entity_uri) > 1 else None)
                if result is not None:
                    for item in result:
                        m = int(item["m"]["value"])
                        uri = entity_uri[1] if len(entity_uri) > 1 else 0
                        if m == 0:
                            n_s = self.create_or_get_node(uri, True)
                            n_d = self.create_or_get_node(entity_uri[0])
                            e = Edge(n_s, relation_uri, n_d)
                            self.add_edge(e)
                        elif m == 1:
                            n_d = self.create_or_get_node(uri, True)
                            n_s = self.create_or_get_node(entity_uri[0])
                            e = Edge(n_s, relation_uri, n_d)
                            self.add_edge(e)
                        # elif m == 2:
                        #     n_d = self.create_or_get_node(relation_uri)
                        #     n_s = self.create_or_get_node(entity_uri[0])
                        #     e = Edge(n_s, uri, n_d)
                        #     # self.add_edge(e)
                        # elif m == 3:
                        #     n_d = self.create_or_get_node(entity_uri[0])
                        #     n_s = self.create_or_get_node(relation_uri)
                        #     e = Edge(n_s, uri, n_d)
                        #     # self.add_edge(e)
                        elif m == 2:
                            n_d = self.create_or_get_node(relation_uri)
                            n_s = self.create_or_get_node(uri)
                            e = Edge(n_s, Uri(self.kb.type_uri, self.kb.parse_uri), n_d)
                            self.add_edge(e)

    def find_minimal_subgraph(self, entity_uris, relation_uris, ask_query=False):
        self.entity_uris, self.relation_uris = MyList(), MyList()
        self.entity_uris.extend(entity_uris)
        self.relation_uris.extend(relation_uris)

        #Find subgraphs that are consist of at leat one entity and exactly one relation
        self.__one_hop_graph(entity_uris, relation_uris, int(ask_query) + 1)

        if len(self.edges) > 100:
            return

        for edge in itertools.islice(self.edges, 0, len(self.edges)):
            mergeable_node = None
            entity_node = None

            if edge.source_node.mergable:
                mergeable_node = edge.source_node
            else:
                entity_node = edge.source_node

            if edge.dest_node.mergable:
                mergeable_node = edge.dest_node
            else:
                entity_node = edge.dest_node

            if mergeable_node is not None and entity_node is not None:
                self.__one_hop_graph(self.entity_uris - entity_node.uris,
                                     self.relation_uris - [e.uri for e in entity_node.inbound + entity_node.outbound])

        # Extend the existing edges with another hop
        self.__extend_edges(self.edges, relation_uris)

    def __extend_edges(self, edges, relation_uris):
        new_edges = set()
        for relation_uri in relation_uris:
            for edge in edges:
                new_edges.update(self.__extend_edge(edge, relation_uri))
        for e in new_edges:
            self.add_edge(e)

    def __extend_edge(self, edge, relation_uri):
        output = set()
        var_node = None
        if edge.source_node.are_all_uris_generic():
            var_node = edge.source_node
        if edge.dest_node.are_all_uris_generic():
            var_node = edge.dest_node
        ent1 = edge.source_node.first_uri_if_only()
        ent2 = edge.dest_node.first_uri_if_only()
        if not (var_node is None or ent1 is None or ent2 is None):
            result = self.kb.two_hop_graph(ent1, edge.uri, ent2, relation_uri)
            if result is not None:
                for item in result:
                    if item[1]:
                        if item[0] == 0:
                            n_s = self.create_or_get_node(1, True)
                            n_d = var_node
                            e = Edge(n_s, relation_uri, n_d)
                            output.add(e)
                        elif item[0] == 1:
                            n_s = var_node
                            n_d = self.create_or_get_node(1, True)
                            e = Edge(n_s, relation_uri, n_d)
                            output.add(e)
                        elif item[0] == 2:
                            n_s = var_node
                            n_d = self.create_or_get_node(1, True)
                            e = Edge(n_s, relation_uri, n_d)
                            output.add(e)
                            self.suggest_retrieve_id = 1
                        elif item[0] == 3:
                            n_s = self.create_or_get_node(1, True)
                            n_d = var_node
                            e = Edge(n_s, relation_uri, n_d)
                            output.add(e)
                        elif item[0] == 4:
                            n_d = self.create_or_get_node(relation_uri)
                            n_s = self.create_or_get_node(1, True)
                            e = Edge(n_s, Uri(self.kb.type_uri, self.kb.parse_uri), n_d)
                            output.add(e)
        return output

    def to_where_statement(self):
        self.__generalize_nodes()
        self.__merge_edges()
        output = []
        paths = self.__find_paths(self.entity_uris, self.relation_uris, self.edges, len(self.relation_uris), [])

        # Prune paths that do not contain all the entities
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

        # Remove duplicate paths
        to_be_removed = set()
        for i in range(len(paths)):
            batch_edges = paths[i]
            for j in range(i + 1, len(paths)):
                other_batch_edges = paths[j]
                if len(batch_edges) == len(other_batch_edges):
                    same_flag = True
                    for edge in batch_edges:
                        if edge not in other_batch_edges:
                            same_flag = False
                            break
                    if same_flag:
                        to_be_removed.add(i)
                        break

        to_be_removed = list(to_be_removed)
        to_be_removed.sort(reverse=True)
        for i in to_be_removed:
            paths.pop(i)

        if len(paths) == 1:
            batch_edges = paths[0]
            max_generic_id = 0
            ids = [edge.max_generic_id() for edge in batch_edges]
            if len(ids) > 0:
                max_generic_id = max(ids)
            if self.suggest_retrieve_id > max_generic_id:
                self.suggest_retrieve_id = max_generic_id
            return [(self.suggest_retrieve_id, [edge.sparql_format(self.kb) for edge in batch_edges])]

        for batch_edges in paths:
            sparql_where = [edge.sparql_format(self.kb) for edge in batch_edges]
            max_generic_id = max([edge.max_generic_id() for edge in batch_edges])
            result = self.kb.query_where(sparql_where, count=True)
            if result is not None:
                result = int(result["results"]["bindings"][0]["callret-0"]["value"])
                if result > 0:
                    output.append((max_generic_id, sparql_where))
        return output

    def __find_paths(self, entity_uris, relation_uris, edges, number_of_left_relations, force_entity=False, output=[]):
        new_output = []

        if number_of_left_relations == 0:
            if len(entity_uris) > 0 and len(self.relation_uris) > 0:
                return self.__find_paths(entity_uris, self.relation_uris, edges, 1, force_entity=True, output=output)
            return output

        for relation in relation_uris:
            for edge in self.__find_edges(edges, relation):
                entities = []
                if not (edge.source_node.are_all_uris_generic() or edge.uri.is_type()):
                    entities.extend(edge.source_node.uris)
                if not (edge.dest_node.are_all_uris_generic() or edge.uri.is_type()):
                    entities.extend(edge.dest_node.uris)

                if force_entity and len(entities) == 0:
                    continue

                if entities <= entity_uris:
                    valid_edges = self.__find_paths(entity_uris - entities, relation_uris - {relation},
                                                          edges - {edge},
                                                          number_of_left_relations - 1,
                                                          force_entity=force_entity,
                                                          output=self.__extend_output(edge, output))
                    new_output.extend(valid_edges)

        return new_output

    def __extend_output(self, new_edge, output):
        new_output = []
        if len(output) == 0:
            output.append([])
        for item in output:
            path = []
            for edge in item:
                if edge.uri == new_edge.uri and \
                        edge.source_node.are_all_uris_generic() and \
                        edge.dest_node.are_all_uris_generic() and \
                        not (new_edge.source_node.are_all_uris_generic() and new_edge.dest_node.are_all_uris_generic()):
                    pass
                else:
                    path.append(edge)
            new_output.append(path + [new_edge])
        return new_output

    def __find_edges(self, edges, uri):
        return [edge for edge in edges if edge.uri == uri or (edge.uri.is_type() and edge.dest_node.has_uri(uri))]

    def __get_generic_uri(self, uri, edges):
        return Uri.generic_uri(uri)

    def __generalize_nodes(self):
        uris = self.entity_uris + self.relation_uris
        for node in self.nodes:
            for uri in node.uris:
                if not (uri in uris or uri.is_generic()):
                    generic_uri = self.__get_generic_uri(uri, node.inbound + node.outbound)
                    node.replace_uri(uri, generic_uri)

    def __merge_edges(self):
        to_be_removed = set()
        for edge_1 in self.edges:
            for edge_2 in self.edges:
                if edge_1 is edge_2 or edge_2 in to_be_removed:
                    continue
                if edge_1 == edge_2:
                    to_be_removed.add(edge_2)
        for item in to_be_removed:
            self.remove_edge(item)

    def __str__(self):
        return "\n".join([edge.full_path() for edge in self.edges])
