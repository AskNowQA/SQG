from collections import Counter


class MyList(list):
    def __init__(self, *args):
        super(MyList, self).__init__(*args)

    def __le__(self, other):
        l1 = Counter(self)
        l2 = Counter(other)
        counts = l1 - l2
        return len(counts) == 0

    def __sub__(self, other):
        try:
            other_ = other
            if isinstance(other, set):
                other_ = list(other)
            l1 = Counter(self)
            l2 = Counter(other_)
            output = []
            counts = l1 - l2
            for item in counts:
                output.extend([item] * counts[item])

            return self.__class__(output)
        except:
            return []
