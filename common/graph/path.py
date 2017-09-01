from node import Node
from edge import Edge
from common.uri import Uri


class Path:
    def __init__(self, source_node, edge, dest_node):
        self.source_node = source_node
        self.edge = edge
        self.dest_node = dest_node

    def merge(self, other_path):
        """
        Try to merge the current path with the other_path recursively
        :param other_path: should be of type common.graph.Path
        :return: True if it succeed
        """
        if self.source_node == other_path.source_node and self.edge == other_path.edge:
            if self.dest_node == other_path.dest_node:
                return True
            elif isinstance(other_path.dest_node, Path) and isinstance(self.dest_node, Node) \
                    and self.dest_node == other_path.dest_node.source_node:
                self.dest_node = other_path.dest_node
                return True
            elif isinstance(other_path.dest_node, Node) and isinstance(self.dest_node, Path) \
                    and other_path.dest_node == self.dest_node.source_node:
                return True

            elif isinstance(other_path.dest_node, Path) and isinstance(self.dest_node, Path):
                return self.dest_node.merge(other_path.dest_node)

        return False

    def contains_answers(self, answers):
        """
        Check if path contains all the answers
        :param answers: should be of type common.Answers
        :return: return True if path contains all the answers
        """
        to_be_removed = []
        for answer in answers:
            if (self.source_node.uri == answer.answer) or (isinstance(self.dest_node, Node) and self.dest_node.uri == answer.answer):
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
                if self.source_node.uri == answer.answer:
                    self.source_node.uri = Uri.generic_uri(var_num)
                    var_num += 1
        if isinstance(self.dest_node, Node):
            for answer_row in answers_set.answer_rows:
                for answer in answer_row.answers:
                    if self.dest_node.uri == answer.answer:
                        self.dest_node.uri = Uri.generic_uri(var_num)
                        var_num += 1
        else:
            self.dest_node.replace_answers(answers_set, var_num)

    def __generate_where(self):
        dest_node = self.dest_node
        if isinstance(self.dest_node, Path):
            dest_node = self.dest_node.source_node
            return u" {} {} {} . {}".format(self.source_node.uri.sparql_format(), self.edge.uri.sparql_format(),
                                       dest_node.uri.sparql_format(), self.dest_node.__generate_where())
        else:
            return u" {} {} {} ".format(self.source_node.uri.sparql_format(), self.edge.uri.sparql_format(), dest_node.uri.sparql_format())

    def generate_sparql(self):
        return u"SELECT DISTINCT * WHERE {{ {} }}".format(self.__generate_where())

    def __str__(self):
        return u"{} --> {} --> {}".format(self.source_node.__str__(), self.edge.__str__(),
                                          self.dest_node.__str__()).encode("ascii", "ignore")

    @staticmethod
    def create_path(uris):
        """
        Create a path from the input URIs
        :param uris: should type of [common.URI]
        :return: common.graph.Path
        """
        if len(uris) == 3:
            source_node = Node(uris[0])
            dest_node = Node(uris[2])
            edge = Edge(source_node, uris[1], dest_node)
            return Path(source_node, edge, dest_node)
        else:
            source_node = Node(uris[0])
            dest_node = Path.create_path(uris[2:])
            edge = Edge(source_node, uris[1], dest_node)
            return Path(source_node, edge, dest_node)
