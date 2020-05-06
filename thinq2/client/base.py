from os import path

from uplink import Consumer


class BaseClient(Consumer):
    """ Base client class """

    def __init__(self, base_url=None, headers={}, **kwargs):
        super().__init__(path.join(base_url or self.base_url, ""), **kwargs)
        self.session.headers.update(headers)
