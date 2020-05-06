from uplink import get

from thinq2.client.base import BaseClient
from thinq2.model.common import Route
from thinq2.model.thinq import ThinQResult


class CommonClient(BaseClient):
    """LG ThinQ Common API client"""

    base_url = "https://common.lgthinq.com/"

    @get("route")
    def get_route(self) -> ThinQResult(Route):
        """Retrieves route definition for current country/language (MQTT url, etc)"""
