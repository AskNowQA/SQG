class LinkedItem:
    def __init__(self, surface_form, uris):
        self.surface_form = surface_form
        self.uris = uris

    def contains_uri(self, uri):
        """
        Whether the uri exists in the list of uris
        :param uri:
        :return: Bool
        """
        return uri in self.uris

    @staticmethod
    def list_contains_uris(linkeditem_list, uris):
        """
        Returns the linkedItems that contain any of the uris,
        but only one linkedItem per uri
        :param linkeditem_list: List of LinkedItem
        :param uris:
        :return:
        """
        output = []
        for uri in uris:
            for item in linkeditem_list:
                if item not in output and item.contains_uri(uri):
                    output.append(item)
                    break
        return output
