from path import Path
import numpy as np


class Paths(list):
    def __init__(self, *args):
        super(Paths, self).__init__(*args)

    @property
    def confidence(self):
        return np.prod([path.confidence for path in self])

    def to_where(self, kb=None):
        output = []
        for batch_edges in self:
            sparql_where = [edge.sparql_format(kb) for edge in batch_edges]
            max_generic_id = max([edge.max_generic_id() for edge in batch_edges])
            if kb is not None:
                result = kb.query_where(sparql_where, count=True)
                if result is not None:
                    result = int(result["results"]["bindings"][0]["callret-0"]["value"])
                    if result > 0:
                        output.append((max_generic_id, sparql_where))
            else:
                output.append((max_generic_id, sparql_where))
        return output

    def add(self, new_paths, validity_fn):
        for path in new_paths:
            if (len(self) == 0 or path not in self) and validity_fn(path):
                self.append(path)

    def extend(self, new_edge):
        new_output = []
        if len(self) == 0:
            self.append(Path([]))
        for item in self:
            path = Path()
            for edge in item:
                if edge.uri == new_edge.uri and \
                        edge.source_node.are_all_uris_generic() and \
                        edge.dest_node.are_all_uris_generic() and \
                        not (new_edge.source_node.are_all_uris_generic() and new_edge.dest_node.are_all_uris_generic()):
                    pass
                else:
                    path.append(edge)
            new_output.append(Path(path + [new_edge]))
        return Paths(new_output)

    def __contains__(self, new_path):
        for i in range(len(self)):
            if len(self[i]) == len(new_path):
                same_flag = True
                for edge in self[i]:
                    if edge not in new_path:
                        same_flag = False
                        break
                if same_flag:
                    return True
        return False
