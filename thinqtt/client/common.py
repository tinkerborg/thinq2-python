from uplink import get

from thinqtt.client.base import BaseClient
from thinqtt.model.common import Route
from thinqtt.model.thinq import ThinQResult


class CommonClient(BaseClient):
    """LG ThinQ Common API client"""

    base_url = "https://common.lgthinq.com/"

    @get("route")
    def get_route(self) -> ThinQResult(Route):
        """Retrieves route definition for current country/language (MQTT url, etc)"""
