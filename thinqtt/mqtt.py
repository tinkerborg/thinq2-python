import requests
import ssl
from urllib.parse import urlparse

from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM
from paho.mqtt.client import Client

from thinqtt.util import create_tempfile, memoize
from thinqtt.model.config import MQTTConfiguration
from thinqtt.schema import controller, initializer
from thinqtt.client.thinq import ThinQClient
from thinqtt.client.common import CommonClient

from thinqtt import AWS_IOTT_CA_CERT_URL, AWS_IOTT_ALPN_PROTOCOL


@controller(MQTTConfiguration)
class ThinQTT:
    def __init__(self, auth):
        self._auth = auth

    def connect(self):
        endpoint = urlparse(self.route.mqtt_server)
        self.client.connect(endpoint.hostname, endpoint.port)

    def loop_start(self):
        self.client.loop_start()

    def loop_forever(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.registration.subscriptions:
            client.subscribe(topic, 1)

    def on_message(self, client, userdata, msg):
        pass

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
        ca_cert = create_tempfile(self.ca_cert)
        private_key = create_tempfile(self.private_key)
        client_cert = create_tempfile(self.registration.certificate_pem)

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.set_alpn_protocols([AWS_IOTT_ALPN_PROTOCOL])
        context.load_cert_chain(certfile=client_cert.name, keyfile=private_key.name)
        context.load_verify_locations(cafile=ca_cert.name)

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
