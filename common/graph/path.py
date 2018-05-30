import numpy as np


class Path(list):
    def __init__(self, *args):
        super(Path, self).__init__(*args)
        self.__sorted_str = None

    @property
    def confidence(self):
        """
        Cumulative product of edges' confidence
        :return:
        """
        return np.prod([edge.confidence for edge in self])

    def addable(self, candidate_edge):
        """
        Whether candidate edge would be connected to the current path
        :param candidate_edge:
        :return:
        """
        if len(self) == 0:
            return True
        for edge in self:
            if edge.uri == candidate_edge.uri or \
                    edge.source_node == candidate_edge.source_node or \
                    edge.dest_node == candidate_edge.dest_node or \
                    edge.source_node == candidate_edge.dest_node or \
                    edge.dest_node == candidate_edge.source_node:
                return True
        return False

    def replace_edge(self, old_edge, new_edge):
        """
        Create a new path in which an existing edge is replaced with the new edge
        :param old_edge:
        :param new_edge:
        :return: None if the old_edge is not in the current path
        """
        try:
            new_path = Path(self)
            new_path[new_path.index(old_edge)] = new_edge
            return new_path
        except ValueError:
            return None

    def __eq__(self, other):
        if len(self) == len(other):
            same_flag = True
            for edge in self:
                if edge not in other:
                    same_flag = False
                    break
            if same_flag:
                return True
        return False

    def generic_equal(self, other):
        return self.__generic_equal(other)[0]

    def generic_equal_with_substitutable_id(self, other):
        output = self.__generic_equal(other)
        if not output[0]:
            return False
        return len(set(output[1])) == 1

    def __generic_equal(self, other):
        """
        Check whether the other path in the same as the current one, perhaps with different generic node id
        :param other:
        :return:
        """
        output = []
        if len(self) == len(other):
            for edge1 in self:
                edge_found = False
                for edge2 in other:
                    if edge1.generic_equal(edge2):
                        edge_found = True
                        if edge1.source_node.generic_equal(
                                edge2.source_node) and edge1.source_node.are_all_uris_generic() \
                                and edge2.source_node.are_all_uris_generic():
                            output.append(
                                frozenset(
                                    [edge1.source_node.first_uri_if_only(), edge2.source_node.first_uri_if_only()]))
                        if edge1.dest_node.generic_equal(
                                edge2.dest_node) and edge1.dest_node.are_all_uris_generic() \
                                and edge2.dest_node.are_all_uris_generic():
                            output.append(
                                frozenset([edge1.dest_node.first_uri_if_only(), edge2.dest_node.first_uri_if_only()]))
                        if edge1.uri.is_generic() and edge1.uri.generic_equal(
                                edge2.uri):
                            output.append(
                                frozenset([edge1.uri, edge2.uri]))
                        break
                if not edge_found:
                    return False, []
            return True, output
        else:
            return False, []

    def __str__(self):
        if self.__sorted_str is None:
            self.__sorted_str = '-'.join(sorted([item.full_path() for item in self]))
        return self.__sorted_str
