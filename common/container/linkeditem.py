class LinkedItem:
    def __init__(self, surface_form, uris):
        self.surface_form = surface_form
        self.uris = uris

    def contains_uris(self, uris):
        return any(uri in uris for uri in self.uris)

    @staticmethod
    def list_contains_uris(linkeditem_list, uris):
        """
        Returns linkedItems that contain any of the uris
        :param linkeditem_list: List of LinkedItem
        :param uris:
        :return:
        """
        return [item for item in linkeditem_list if item.contains_uris(uris)]
