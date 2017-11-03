import numpy as np


class Path(list):
    def __init__(self, *args):
        super(Path, self).__init__(*args)

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
