import requests
from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM

from thinqtt.auth import ThinQTTAuth
from thinqtt.model.mqtt import MQTTConfiguration
from thinqtt.schema import controller, initializer
from thinqtt.client.thinq import ThinQClient
from thinqtt.client.common import CommonClient

from thinqtt import AWS_IOTT_CA_CERT_URL


@controller(MQTTConfiguration, auth=ThinQTTAuth)
class ThinQTT:
    @property
    def thinq_client(self):
        return ThinQClient(base_url=self.auth.gateway.thinq2_uri, auth=self.auth)

    @property
    def common_client(self):
        return CommonClient(auth=self.auth)

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
