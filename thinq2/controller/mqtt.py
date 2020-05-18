import requests
import ssl
from urllib.parse import urlparse

from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM
from paho.mqtt.client import Client

from thinq2.model.mqtt import MQTTConfiguration, MQTTMessage
from thinq2.schema import controller, initializer
from thinq2.client.thinq import ThinQClient
from thinq2.client.common import CommonClient
from thinq2.util import memoize
from thinq2.util.filesystem import TempDir

from thinq2 import AWS_IOTT_CA_CERT_URL, AWS_IOTT_ALPN_PROTOCOL


@controller(MQTTConfiguration)
class ThinQMQTT:
    def __init__(self, auth):
        self._auth = auth

    def connect(self):
        if not self.client.is_connected():
            endpoint = urlparse(self.route.mqtt_server)
            self.client.connect(endpoint.hostname, endpoint.port)

    def loop_start(self):
        self.connect()
        self.client.loop_start()

    def loop_forever(self):
        self.connect()
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        self._on_message(client, userdata, msg)

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.registration.subscriptions:
            client.subscribe(topic, 1)

    def on_device_message(self, message):
        pass

    def _on_message(self, client, userdata, msg):
        # XXX - nastiness
        message = None
        try:
            message = MQTTMessage.Schema().loads(msg.payload)
        except Exception as e:
            print("Can't parse MQTT message:", e)
        self.on_device_message(message)

    @property
    @memoize
    def client(self):
        client = Client(client_id=self._auth.client_id)
        client.tls_set_context(self.ssl_context)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        return client

    @property
    @memoize
    def thinq_client(self):
        return ThinQClient(base_url=self._auth.gateway.thinq2_uri, auth=self._auth)

    @property
    @memoize
    def common_client(self):
        return CommonClient(auth=self._auth)

    @property
    def ssl_context(self):
        temp_dir = TempDir()
        ca_cert_path = temp_dir.file(self.ca_cert)
        private_key_path = temp_dir.file(self.private_key)
        client_cert_path = temp_dir.file(self.registration.certificate_pem)

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.set_alpn_protocols([AWS_IOTT_ALPN_PROTOCOL])
        context.load_verify_locations(cafile=ca_cert_path)
        context.load_cert_chain(certfile=client_cert_path, keyfile=private_key_path)

        return context

    @initializer
    def ca_cert(self):
        return requests.get(AWS_IOTT_CA_CERT_URL).text

    @initializer
    def private_key(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        return str(crypto.dump_privatekey(FILETYPE_PEM, key), "utf8")

    @initializer
    def csr(self):
        key = crypto.load_privatekey(FILETYPE_PEM, self.private_key)
        csr = crypto.X509Req()
        csr.get_subject().CN = "AWS IoT Certificate"
        csr.get_subject().O = "Amazon"
        csr.set_pubkey(key)
        csr.sign(key, "sha256")
        return str(crypto.dump_certificate_request(FILETYPE_PEM, csr), "utf8")

    @initializer
    def registration(self):
        if self.thinq_client.get_registered() is False:
            self.thinq_client.register()
        return self.thinq_client.register_iot(csr=self.csr)

    @initializer
    def route(self):
        return self.common_client.get_route()
