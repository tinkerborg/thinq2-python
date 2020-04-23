from uplink import get

from thinqtt.client.base import BaseClient
from thinqtt.schema import ThinQResponse
from thinqtt.model.gateway import Gateway


class GatewayClient(BaseClient):
    """LG ThinQ Gateway API client"""

    base_url = "https://route.lgthinq.com:46030/v1/"

    @get("service/application/gateway-uri")
    def get_gateway(self) -> ThinQResponse.wrap(Gateway):
        """Retrieves Gateway information for current country/language"""
