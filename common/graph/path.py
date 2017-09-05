from node import Node
from edge import Edge
from common.uri import Uri
import sys


class Path:
    def __init__(self, source_node, source_to_dest_edge, dest_to_source_edge, dest_node):
        self.source_node = source_node
        self.source_to_dest_edge = source_to_dest_edge
        self.dest_to_source_edge = dest_to_source_edge
        self.dest_node = dest_node

    def copy(self):
        return Path(self.source_node, self.source_to_dest_edge, self.dest_to_source_edge, self.dest_node)

    def expand(self, other_path):
        if isinstance(other_path.dest_node, Node) and isinstance(self.dest_node, Node) \
             and self.dest_node == other_path.dest_node\
             and not self.contains_node(other_path.source_node):
            new_path = self.copy()
            new_path.dest_node = Path(self.dest_node, None, other_path.source_to_dest_edge, other_path.source_node)
            return new_path
        return None

    def merge(self, other_path):
        """
        Try to merge the current path with the other_path recursively
        :param other_path: should be of type common.graph.Path
        :return: True if it succeed
        """
        if (self.source_to_dest_edge == other_path.source_to_dest_edge and self.source_to_dest_edge is not None) or \
                (self.dest_to_source_edge == other_path.dest_to_source_edge and self.dest_to_source_edge is not None):
            if self.source_node == other_path.source_node:
                if self.dest_node == other_path.dest_node:
                    return True
                elif isinstance(other_path.dest_node, Path) and isinstance(self.dest_node, Node) \
                        and self.dest_node.mergable and self.dest_node <= other_path.dest_node.source_node:
                    self.dest_node = other_path.dest_node
                    return True

                elif isinstance(other_path.dest_node, Node) and isinstance(self.dest_node, Path) \
                        and other_path.dest_node.mergable and other_path.dest_node <= self.dest_node.source_node:
                    return True

                elif isinstance(other_path.dest_node, Path) and isinstance(self.dest_node, Path):
                    return self.dest_node.merge(other_path.dest_node)

                elif isinstance(other_path.dest_node, Node) and isinstance(self.dest_node, Node) \
                        and self.dest_node.mergable and other_path.dest_node.mergable:
                    self.dest_node = Node([self.dest_node.uris, other_path.dest_node.uris], True)
                    return True
            else:
                if isinstance(other_path.source_node, Node) and isinstance(self.source_node, Node) \
                        and self.source_node.mergable and other_path.source_node.mergable \
                        and isinstance(other_path.dest_node, Node) and isinstance(self.dest_node, Node):
                    if self.dest_node.mergable and other_path.dest_node.mergable:
                        self.source_node = Node([self.source_node.uris, other_path.source_node.uris], True)
                        self.dest_node = Node([self.dest_node.uris, other_path.dest_node.uris], True)
                        return True
                    elif self.dest_node == other_path.dest_node:
                        self.source_node = Node([self.source_node.uris, other_path.source_node.uris], True)
                        return True

        return False

    def contains_node(self, node):
        if self.source_node == node:
            return True
        if isinstance(self.dest_node, Node):
            if self.dest_node == node:
                return True
        elif isinstance(self.dest_node, Path):
            return self.dest_node.contains_node(node)
        return False

    def contains_answers(self, answers):
        """
        Check if path contains all the answers
        :param answers: should be of type common.Answers
        :return: return True if path contains all the answers
        """
        to_be_removed = []
        for answer in answers:
            if (self.source_node.has_uri(answer.answer)) or (isinstance(self.dest_node, Node) and self.dest_node.has_uri(answer.answer)):
                to_be_removed.append(answer)

        answers = [answer for answer in answers if answer not in to_be_removed]
        if len(answers) > 0:
            if isinstance(self.dest_node, Path):
                return self.dest_node.contains_answers(answers)
            else:
                return False
        return True

    def replace_answers(self, answers_set, var_num=1):
        """
        Replace the nodes with answers' URI with a generic one
        :param answers_set:
        :param var_num:
        :return:
        """
        for answer_row in answers_set.answer_rows:
            for answer in answer_row.answers:
                if self.source_node.replace_uri(answer.answer, Uri.generic_uri(var_num)):
                    var_num += 1
        if isinstance(self.dest_node, Node):
            for answer_row in answers_set.answer_rows:
                for answer in answer_row.answers:
                    if self.dest_node.replace_uri(answer.answer, Uri.generic_uri(var_num)):
                        var_num += 1
        else:
            self.dest_node.replace_answers(answers_set, var_num)

    def __generate_where(self):
        dest_node = self.dest_node
        if isinstance(self.dest_node, Path):
            dest_node = self.dest_node.source_node
            return u" {} {} {} . {}".format(self.source_node.sparql_format(), self.source_to_dest_edge.sparql_format(),
                                            dest_node.sparql_format(), self.dest_node.__generate_where())
        else:
            if self.dest_to_source_edge is None:
                return u" {} {} {} ".format(self.source_node.sparql_format(), self.source_to_dest_edge.sparql_format(), dest_node.sparql_format())
            else:
                return u" {} {} {} ".format(self.dest_node.sparql_format(),
                                            self.dest_to_source_edge.sparql_format(), self.source_node.sparql_format())

    def generate_sparql(self):
        try:
            return u"SELECT DISTINCT * WHERE {{ {} }}".format(self.__generate_where())
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return None

    def __str__(self):
        if self.dest_to_source_edge is None:
            return u"{} --> {} --> {}".format(self.source_node.__str__(), self.source_to_dest_edge.__str__(),
                                          self.dest_node.__str__()).encode("ascii", "ignore")
        else:
            return u"{} <-- {} <-- {}".format(self.source_node.__str__(), self.dest_to_source_edge.__str__(),
                                          self.dest_node.__str__()).encode("ascii", "ignore")

    @staticmethod
    def create_path(uris, is_answer):
        """
        Create a path from the input URIs
        :param uris: should type of [common.URI]
        :return: common.graph.Path
        """
        mergable = lambda uri: True if is_answer(uri) else False

        if len(uris) == 3:
            source_node = Node(uris[0], mergable(uris[0]))
            dest_node = Node(uris[2], mergable(uris[2]))
            edge = Edge(source_node, uris[1], dest_node)
            return Path(source_node, edge, None, dest_node)
        else:
            source_node = Node(uris[0], mergable(uris[0]))
            dest_node = Path.create_path(uris[2:], is_answer)
            edge = Edge(source_node, uris[1], dest_node)
            return Path(source_node, edge, None, dest_node)
