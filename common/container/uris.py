class URIs(list):
    def __init__(self, *args):
        super(URIs, self).__init__(*args)

    def __eq__(self, other):
        if isinstance(other, URIs):
            if len(self) != len(other):
                return False
            for uri in self:
                found = False
                for other_uri in other:
                    if uri.generic_equal(other_uri):
                        found = True
                        break
                if not found:
                    return False
            return True
        return NotImplemented
