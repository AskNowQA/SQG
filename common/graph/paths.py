class Paths:
    def __init__(self, paths=[]):
        self.paths = paths

    def add(self, new_paths, validity_fn):
        for path in new_paths.paths:
            if (len(self.paths) == 0 or path not in self) and validity_fn(path):
                self.paths.append(path)

    def extend(self, new_edge):
        new_output = []
        if len(self.paths) == 0:
            self.paths.append([])
        for item in self.paths:
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
        return Paths(new_output)

    def __contains__(self, new_path):
        for i in range(len(self.paths)):
            if len(self.paths[i]) == len(new_path):
                same_flag = True
                for edge in self.paths[i]:
                    if edge not in new_path:
                        same_flag = False
                        break
                if same_flag:
                    return True
        return False
