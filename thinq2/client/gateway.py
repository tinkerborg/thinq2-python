from uplink import get

from thinq2.client.base import BaseClient
from thinq2.model.gateway import Gateway
from thinq2.model.thinq import ThinQResult


class GatewayClient(BaseClient):
    """LG ThinQ Gateway API client"""

    base_url = "https://route.lgthinq.com:46030/v1/"

    @get("service/application/gateway-uri")
    def get_gateway(self) -> ThinQResult(Gateway):
        """Retrieves Gateway information for current country/language"""
