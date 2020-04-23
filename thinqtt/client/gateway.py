from uplink import Consumer, Header, get, headers

from thinqtt.client.base import BaseClient
from thinqtt.schema import ThinQResponse
from thinqtt.model.gateway import Gateway


class GatewayClient(BaseClient):
    """A Python Client for the GitHub API."""

    base_url = "https://route.lgthinq.com:46030/v1/"

    @get("service/application/gateway-uri")
    def get_gateway(self) -> ThinQResponse(Gateway):
        """Retrieves the user's public repositories."""
