from uplink import Field
from uplink import get, post, delete, json

from thinqtt.client.base import BaseClient
from thinqtt.model.thinq import (
    ThinQResult,
    ThinQResultSuccess,
    DeviceCollection,
    IOTRegistration,
)


class ThinQClient(BaseClient):
    """LG ThinQ API client"""

    @get("service/application/dashboard")
    def get_devices(self) -> ThinQResult(DeviceCollection):
        """Retrieves collection of user's registered devices"""

    @get("service/users/client")
    def get_registered(self) -> ThinQResultSuccess():
        """Get client registration status"""

    @post("service/users/client")
    def register(self) -> ThinQResultSuccess():
        """Register client ID"""

    @delete("service/users/client")
    def deregister(self) -> ThinQResultSuccess():
        """Deregister client ID"""

    @json
    @post("service/users/client/certificate")
    def register_iot(self, csr: Field) -> ThinQResult(IOTRegistration):
        """Deregister client ID"""
