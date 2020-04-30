from uplink import get

from thinqtt.client.base import BaseClient
from thinqtt.model.gateway import Gateway
from thinqtt.model.thinq import ThinQResult


class GatewayClient(BaseClient):
    """LG ThinQ Gateway API client"""

    base_url = "https://route.lgthinq.com:46030/v1/"

    @get("service/application/gateway-uri")
    def get_gateway(self) -> ThinQResult(Gateway):
        """Retrieves Gateway information for current country/language"""
