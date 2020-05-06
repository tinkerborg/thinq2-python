from thinqtt.mqtt import ThinQTT
from thinqtt.auth import ThinQTTAuth
from thinqtt.model.config import ThinQConfiguration
from thinqtt.schema import controller


@controller(ThinQConfiguration)
class ThinQ:
    @controller
    def auth(self, auth):
        return ThinQTTAuth(auth)

    @controller
    def mqtt(self, mqtt):
        return ThinQTT(mqtt, auth=self.auth)
