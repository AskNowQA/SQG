class Stats:
    def __init__(self):
        self.dict = dict()

    def __getitem__(self, key):
        return self.dict[key]

    def inc(self, key):
        if key not in self.dict:
            self.dict[key] = 0
        self.dict[key] += 1

    def __str__(self):
        return " ".join([key + ":" + str(self.dict[key]) for key in self.dict])
