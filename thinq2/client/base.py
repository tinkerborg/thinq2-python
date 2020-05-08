from uplink import Consumer

from thinq2.util import end_with


class BaseClient(Consumer):
    """ Base client class """

    def __init__(self, base_url=None, headers={}, **kwargs):
        super().__init__(end_with(base_url or self.base_url, "/"), **kwargs)
        self.session.headers.update(headers)
