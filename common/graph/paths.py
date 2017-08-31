class Paths:
    def __init__(self):
        self.paths = []

    def merge_paths(self):
        if len(self.paths) > 1:
            k = 0
            while k < len(self.paths):
                first_path = self.paths[k]
                for i in range(len(self.paths) - 1, 0, -1):
                    if first_path.merge(self.paths[i]):
                        del self.paths[i]
                k += 1


    def add_path(self, new_path):
        """
        Add or merge the new path into the existing paths
        :param new_path: should be of type common.graph.Path
        :return: Returns False if the new path merged into an existing path.
        and returns True if the new path was added to the list of paths
        """
        for path in self.paths:
            if path.merge(new_path):
                return False
        self.paths.append(new_path)
        return True

    def prune_paths(self, answers_set):
        """
        Prune the paths that do not contain the a full answer
        :param answers_set: set of answers
        :return: number of pruned paths
        """
        to_be_removed = []
        for path in self.paths:
            should_remove = True
            for answers in answers_set.answers:
                if path.contains_answers(answers):
                    should_remove = False
                    break
            if should_remove:
                to_be_removed.append(path)
        self.paths = [path for path in self.paths if path not in to_be_removed]
        return len(to_be_removed)

    def replace_answers(self, answers_set):
        """
        Replace the nodes with answers' URI with a generic one
        :param answers:
        :return: None
        """
        for path in self.paths:
            path.replace_answers(answers_set)
