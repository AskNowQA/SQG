import os
import json
import logging.config
import pickle


class PersistanceDict(dict):
    def __init__(self, *args, **kwargs):
        super(PersistanceDict, self).__init__(*args, **kwargs)

    def save(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)  # , pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(file_name):
        with open(file_name, 'rb') as f:
            return pickle.load(f,encoding='latin1')


def makedirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return None


def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def closest_string(text, list_of_text):
    min = len(text) * 100
    idx = -1
    for item in list_of_text:
        value = __levenshtein(text, list_of_text[item])
        if min > value:
            min = value
            idx = item
    return idx


def find_mentions(text, uris):
    output = []
    for uri in uris:
        s, e, dist = __substring_with_min_levenshtein_distance(str(uri), text)
        if dist <= 5:
            output.append({"uri": uri, "start": s, "end": e})
    return output


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


def __min_farest(values):
    return -min((x, -i) for i, x in enumerate(values))[1]


def __min_nearest(values):
    return min(enumerate(values), key=lambda p: p[1])[0]


def __levenshtein(s1, s2):
    if len(s1) < len(s2):
        return __levenshtein(s2, s1)

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


def __substring_with_min_levenshtein_distance(n, h):
    n = n.lower().replace("_", " ")
    h = h.lower()
    row = __fuzzy_substring(n, h)
    end = min(__min_farest(row), len(h) - 1)
    row_rev = __fuzzy_substring(n[::-1], h[::-1])
    start = max(0, len(h) - __min_nearest(row_rev) - 1)

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
