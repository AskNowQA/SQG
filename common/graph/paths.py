class Paths:
    def __init__(self):
        self.paths = []

    def expand_paths(self):
        if len(self.paths) > 1:
            k = 0
            new_paths = []
            while k < len(self.paths):
                first_path = self.paths[k]
                for i in range(len(self.paths) - 1, k, -1):
                    new_path = first_path.expand(self.paths[i])
                    if new_path is not None:
                        new_paths.append(new_path)
                k += 1

            self.paths.extend(new_paths)

    def merge_paths(self):
        if len(self.paths) > 1:
            k = 0
            while k < len(self.paths):
                first_path = self.paths[k]
                for i in range(len(self.paths) - 1, k, -1):
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
        Prune the paths that do not contain the a full answer set
        :param answers_set: answer set
        :return: number of pruned paths
        """
        to_be_removed = []
        for path in self.paths:
            if answers_set.number_of_answer() == 1:
                should_remove = False
                for answer_row in answers_set.answer_rows:
                    if not path.contains_answers(answer_row.answers):
                        should_remove = True
                        break
                if should_remove:
                    to_be_removed.append(path)
            else:
                should_remove = True
                for answer_row in answers_set.answer_rows:
                    if path.contains_answers(answer_row.answers):
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
