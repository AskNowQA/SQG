class WordHashing:
    def __init__(self):
        self.ids = {}

    def to_n_gams(self, text, n=3):
        text = text.lower()
        words = "".join([x if (('a' <= x <= 'z') or x == ' ') else ' ' for x in text])
        words = words.split()
        res = []
        for word in words:
            padded_word = "#{}#".format(word)
            seq = []
            for i in range(n):
                seq.append(padded_word[i:])
            n_tuples = zip(*seq)
            seq = ["".join(x) for x in n_tuples]
            res.extend(seq)
        return res

    def __encode_n_grams(self, input):
        ids = []
        for term in input:
            if term in self.ids:
                ids.append(self.ids[term])
            else:
                term_id = len(self.ids)
                self.ids[term] = term_id
                ids.append(term_id)
        return ids

    def hash(self, text, n=3):
        return self.__encode_n_grams(self.to_n_gams(text, n))

    def save(self, path):
        with open(path, 'w') as dict_file:
            for kv in self.ids.iteritems():
                dict_file.write('{} {}\n'.format(kv[0], kv[1]))
            dict_file.close()

    def load(self, path):
        self.ids = {}
        with open(path) as dict_file:
            for line in dict_file:
                kv = line.strip("\n").split(" ")
                self.ids[kv[0]] = int(kv[1])
