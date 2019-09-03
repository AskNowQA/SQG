from tqdm import tqdm
import numpy as np
from common.graph.path import Path


class Paths(list):
    def __init__(self, *args):
        super(Paths, self).__init__(*args)

    @property
    def confidence(self):
        """
        Cumulative product of paths' confidence
        :return:
        """
        return np.prod([path.confidence for path in self])

    def to_where(self, kb=None, ask_query=False):
        """
        Transform paths into where clauses
        :param kb:
        :param ask_query:
        :return:
        """

        output = []
        if kb is None or ask_query:
            for batch_edges in tqdm(self):
                sparql_where = [edge.sparql_format(kb) for edge in batch_edges]
                max_generic_id = max([edge.max_generic_id() for edge in batch_edges])
                output.append({"suggested_id": max_generic_id, "where": sparql_where})

        queries = list(self)
        for start_idx in tqdm(range(0, len(queries), 10)):
            batch_queries = [[idx, " .".join([edge.sparql_format(kb) for edge in batch_edges])] for idx, batch_edges in
                             enumerate(queries[start_idx:start_idx + 10])]
            batch_output = kb.parallel_query(batch_queries)
            for id, result in batch_output:
                if result:
                    max_generic_id = max([edge.max_generic_id() for edge in self[id + start_idx]])
                    sparql_where = batch_queries[id][1]
                    output.append({"suggested_id": max_generic_id, "where": sparql_where})

        return output

    def add(self, new_paths, validity_fn):
        """
        Append new paths if they pass the validity check
        :param new_paths:
        :param validity_fn:
        :return:
        """
        for path in new_paths:
            if (len(self) == 0 or path not in self) and validity_fn(path):
                self.append(path)

    def extend(self, new_edge):
        """
        Create a new <Paths> that contains path of current <Paths> which the new_edge if possible is appended to each
        :param new_edge:
        :return:
        """
        new_output = []
        if len(self) == 0:
            self.append(Path([]))
        for item in self:
            if item.addable(new_edge):
                path = Path()
                for edge in item:
                    if edge.uri == new_edge.uri and \
                            edge.source_node.are_all_uris_generic() and \
                            edge.dest_node.are_all_uris_generic() and \
                            not (
                                    new_edge.source_node.are_all_uris_generic() and new_edge.dest_node.are_all_uris_generic()):
                        pass
                    else:
                        path.append(edge)
                new_output.append(Path(path + [new_edge]))
            else:
                new_output.append(item)
        return Paths(new_output)

    def remove_duplicates(self):
        removed_duplicate_paths = []
        paths_str = [str(path) for path in self]
        for idx in range(len(self)):
            if paths_str[idx] not in paths_str[idx + 1:]:
                removed_duplicate_paths.append(self[idx])

        return Paths(removed_duplicate_paths)
