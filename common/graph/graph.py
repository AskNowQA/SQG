from common.graph.node import Node
from common.graph.edge import Edge
from common.container.uri import Uri
from common.container.linkeditem import LinkedItem
from common.utility.mylist import MyList
import itertools
import logging
from tqdm import tqdm


class Graph:
    def __init__(self, kb, logger=None):
        self.kb = kb
        self.logger = logger or logging.getLogger(__name__)
        self.nodes, self.edges = set(), set()
        self.entity_items, self.relation_items = [], []
        self.suggest_retrieve_id = 0

    def create_or_get_node(self, uris, mergable=False):
        if isinstance(uris, (int)):
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

    def count_combinations(self, entity_items, relation_items, number_of_entities, top_uri):
        total = 0
        for relation_item in relation_items:
            rel_uris_len = len(relation_item.top_uris(top_uri))
            for entity_uris in itertools.product(*[items.top_uris(top_uri) for items in entity_items]):
                total += rel_uris_len * len(list(itertools.combinations(entity_uris, number_of_entities)))
        return total

    def __one_hop_graph(self, entity_items, relation_items, threshold=None, number_of_entities=1):
        top_uri = 1

        total = self.count_combinations(entity_items, relation_items, number_of_entities, top_uri)
        if threshold is not None:
            while total > threshold:
                top_uri -= 0.1
                total = self.count_combinations(entity_items, relation_items, number_of_entities, top_uri)

        with tqdm(total=total, disable=self.logger.level >= 10) as pbar:
            for relation_item in relation_items:
                for relation_uri in relation_item.top_uris(top_uri):
                    for entity_uris in itertools.product(*[items.top_uris(top_uri) for items in entity_items]):
                        for entity_uri in itertools.combinations(entity_uris, number_of_entities):
                            pbar.update(1)
                            result = self.kb.one_hop_graph(entity_uri[0], relation_uri,
                                                           entity_uri[1] if len(entity_uri) > 1 else None)
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
                                        n_s = self.create_or_get_node(entity_uri[0])
                                        n_d = self.create_or_get_node(uri, True)
                                        e = Edge(n_s, relation_uri, n_d)
                                        self.add_edge(e)
                                    elif m == 2:
                                        n_s = self.create_or_get_node(uri)
                                        n_d = self.create_or_get_node(relation_uri)
                                        e = Edge(n_s, Uri(self.kb.type_uri, self.kb.parse_uri), n_d)
                                        self.add_edge(e)

    def find_minimal_subgraph(self, entity_items, relation_items, double_relation=False, ask_query=False,
                              sort_query=False, h1_threshold=None):
        self.entity_items, self.relation_items = MyList(entity_items), MyList(relation_items)

        if double_relation:
            self.relation_items.append(self.relation_items[0])

        # Find subgraphs that are consist of at least one entity and exactly one relation
        # self.logger.info("start finding one hop graph")
        self.__one_hop_graph(self.entity_items, self.relation_items, number_of_entities=int(ask_query) + 1,
                             threshold=h1_threshold)
        # self.logger.info("finding one hop graph finished")

        if len(self.edges) > 100:
            return

        # Extend the existing edges with another hop
        # self.logger.info("Extend edges with another hop")
        self.__extend_edges(self.edges, relation_items)

    def __extend_edges(self, edges, relation_items):
        new_edges = set()
        total = 0
        for relation_item in relation_items:
            for relation_uri in relation_item.uris:
                total += len(edges)
        with tqdm(total=total, disable=self.logger.level >= 10) as pbar:
            for relation_item in relation_items:
                for relation_uri in relation_item.uris:
                    for edge in edges:
                        pbar.update(1)
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

    def __get_generic_uri(self, uri, edges):
        return Uri.generic_uri(uri)

    def generalize_nodes(self):
        """
        if there are nodes which have none-generic uri that is not in the list of possible entity/relation,
        such uris will be replaced by a generic uri
        :return: None
        """
        uris = sum([items.uris for items in self.entity_items] + [items.uris for items in self.relation_items], [])
        for node in self.nodes:
            for uri in node.uris:
                if uri not in uris and not uri.is_generic():
                    generic_uri = self.__get_generic_uri(uri, node.inbound + node.outbound)
                    node.replace_uri(uri, generic_uri)

    def merge_edges(self):
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
