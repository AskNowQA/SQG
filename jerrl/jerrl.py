import itertools
from common.linkeditem import LinkedItem
from common.uri import Uri


class Jerrl:
    def __init__(self):
        pass

    def do(self, qapair):
        return [u for u in qapair.sparql.uris if u.is_entity()], \
               [u for u in qapair.sparql.uris if u.is_ontology()]

    def find_mentions(self, text, uris):
        output = []
        for uri in uris:
            s, e, dist = Jerrl.__substring_with_min_levenshtein_distance(str(uri), text)
            if dist <= 5:
                output.append({"uri": uri, "start": s, "end": e})
        return output

    @staticmethod
    def __fuzzy_substring(needle, haystack):
        """Calculates the fuzzy match of needle in haystack,
        using a modified version of the Levenshtein distance
        algorithm.
        The function is modified from the levenshtein function
        in the bktree module by Adam Hupp"""
        m, n = len(needle), len(haystack)

        # base cases
        if m == 1:
            # return not needle in haystack
            row = [len(haystack)] * len(haystack)
            row[haystack.find(needle)] = 0
            return row
        if not n:
            return m

        row1 = [0] * (n + 1)
        for i in range(0, m):
            row2 = [i + 1]
            for j in range(0, n):
                cost = (needle[i] != haystack[j])

                row2.append(min(row1[j + 1] + 1,  # deletion
                                row2[j] + 1,  # insertion
                                row1[j] + cost)  # substitution
                            )
            row1 = row2
        return row1

    @staticmethod
    def __min_farest(values):
        return -min((x, -i) for i, x in enumerate(values))[1]

    @staticmethod
    def __min_nearest(values):
        return min(enumerate(values), key=lambda p: p[1])[0]

    @staticmethod
    def __levenshtein(s1, s2):
        if len(s1) < len(s2):
            return Jerrl.__levenshtein(s2, s1)

        # len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[
                                 j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1  # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def __substring_with_min_levenshtein_distance(n, h):
        n = n.lower().replace("_", " ")
        h = h.lower()
        row = Jerrl.__fuzzy_substring(n, h)
        end = min(Jerrl.__min_farest(row), len(h) - 1)
        row_rev = Jerrl.__fuzzy_substring(n[::-1], h[::-1])
        start = max(0, len(h) - Jerrl.__min_nearest(row_rev) - 1)

        strip = [" ", "?", ".", ",", "'"]
        # stretch the token to be whole word[s]
        while h[start] not in strip and start >= 0:
            start -= 1

        while h[end - 1] not in strip and end < (len(h) - 1):
            end += 1

        # remove invalid chars in head or tail
        for i in range(start, end):
            if h[start] in strip:
                start += 1
            else:
                break

        for i in range(end, start, -1):
            if h[end - 1] in strip:
                end -= 1
            else:
                break

        return start, end, row[end]
