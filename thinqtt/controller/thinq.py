from thinqtt.schema import controller
from thinqtt.util import memoize
from thinqtt.client.thinq import ThinQClient
from thinqtt.controller.mqtt import ThinQMQTT
from thinqtt.controller.auth import ThinQAuth
from thinqtt.controller.device import ThinQDevice
from thinqtt.model.config import ThinQConfiguration


@controller(ThinQConfiguration)
class ThinQ:
    def get_device(self, device_id):
        return ThinQDevice(self.thinq_client.get_device(device_id), auth=self.auth)

    @property
    @memoize
    def thinq_client(self):
        return ThinQClient(base_url=self.auth.gateway.thinq2_uri, auth=self.auth)

    @controller
    def auth(self, auth):
        return ThinQAuth(auth)

    @controller
    def mqtt(self, mqtt):
        return ThinQMQTT(mqtt, auth=self.auth)
