from deepmerge import Merger

from thinq2.schema import controller
from thinq2.util import memoize
from thinq2.client.thinq import ThinQClient
from thinq2.client.objectstore import ObjectStoreClient
from thinq2.model.thinq import DeviceDescriptor, ModelJsonDataclass


@controller(DeviceDescriptor)
class ThinQDevice:
    def __init__(self, auth):
        self._auth = auth
        self._on_update = None

    def update(self, state):
        schema = self.snapshot.Schema()
        snapshot = schema.dump(self.snapshot)
        update = self._merger.merge(snapshot, state)
        self.snapshot = schema.load(update)
        if self._on_update:
            self._on_update(self)

    def on_update(self, func):
        self._on_update = func

    @property
    def _merger(self):
        return Merger([(dict, ["merge"])], ["override"], ["override"])

    @property
    def state(self):
        return self._model.Schema().load(self.snapshot.state)

    @property
    @memoize
    def model_json(self):
        return self._object_store_client.get_json_url(self.model_json_uri)

    @property
    @memoize
    def model_json_uri(self):
        descriptor = self._thinq_client.get_model_json_descriptor(
            device_id=self.device_id, model_name=self.model_name
        )
        return descriptor.model_json_uri

    @property
    @memoize
    def _model(self):
        return ModelJsonDataclass(self.model_json).build(self.alias)

    @property
    def _thinq_client(self):
        return ThinQClient(base_url=self._auth.gateway.thinq2_uri, auth=self._auth)

    @property
    def _object_store_client(self):
        return ObjectStoreClient()
