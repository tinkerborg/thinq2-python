import gc

from thinq2.schema import controller
from thinq2.util import memoize
from thinq2.client.thinq import ThinQClient
from thinq2.controller.mqtt import ThinQMQTT
from thinq2.controller.auth import ThinQAuth
from thinq2.controller.device import ThinQDevice
from thinq2.model.config import ThinQConfiguration
from thinq2.model.mqtt import MQTTMessage


@controller(ThinQConfiguration)
class ThinQ:

    _devices = []

    def get_device(self, device_id):
        device = ThinQDevice(self.thinq_client.get_device(device_id), auth=self.auth)
        self._devices.append(device)
        return device

    # XXX - temporary?
    def start(self):
        self.mqtt.on_device_message = self._notify_device
        self.mqtt.loop_forever()

    def _notify_device(self, message: MQTTMessage):
        # XXX - ugly temporary PoC
        for device in self._devices:
            if len(gc.get_referrers(device)) <= 1:
                self._devices.remove(device)
            elif device.device_id == message.device_id:
                device.update(message.data.state.reported)

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
