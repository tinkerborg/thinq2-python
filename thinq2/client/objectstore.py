from uplink import Url, get, returns

from thinq2.client.base import BaseClient


class ObjectStoreClient(BaseClient):
    """LG ThinQ API client"""

    base_url = "https://objectstore.lgthinq.com"

    @returns.json
    @get
    def get_json_url(self, url: Url):
        """Retrieves an arbitrary JSON object"""
