from thinq2.schema import controller
from thinq2.util import memoize
from thinq2.client.thinq import ThinQClient
from thinq2.controller.mqtt import ThinQMQTT
from thinq2.controller.auth import ThinQAuth
from thinq2.controller.device import ThinQDevice
from thinq2.model.config import ThinQConfiguration


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
