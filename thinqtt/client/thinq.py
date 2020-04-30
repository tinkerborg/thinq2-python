from uplink import get

from thinqtt.client.base import BaseClient
from thinqtt.model.thinq import DeviceCollection, ThinQResult, ThinQResultSuccess


class ThinQClient(BaseClient):
    """LG ThinQ API client"""

    @get("service/application/dashboard")
    def get_devices(self) -> ThinQResult(DeviceCollection):
        """Retrieves collection of user's registered devices"""

    @get("service/users/client")
    def get_registered(self) -> ThinQResultSuccess():
        """Get client registration status"""
