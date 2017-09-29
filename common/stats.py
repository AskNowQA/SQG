class Stats:
    def __init__(self):
        self.dict = dict()

    def __getitem__(self, key):
        if key not in self.dict:
            return 0
        return self.dict[key]

    def inc(self, key):
        if key not in self.dict:
            self.dict[key] = 0
        self.dict[key] += 1

    def __str__(self):
        keys = self.dict.keys()
        keys.sort()
        return " ".join([key + ":" + str(self.dict[key]) for key in keys])
