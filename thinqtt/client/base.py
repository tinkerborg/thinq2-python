from uplink import Consumer, Header

from thinqtt import ThinQTT
from thinqtt.util.uuid import ThinQMessageID


class BaseClient(Consumer):
    """A Python Client for the GitHub API."""

    def __init__(
        self,
        client_id: Header("x-client-id"),
        country_code: Header("x-country-code"),
        language_code: Header("x-language-code"),
        api_key: Header("x-api-key") = ThinQTT.API_KEY,
        service_code: Header("x-service-code") = ThinQTT.SERVICE_CODE,
        service_phase: Header("x-service-phase") = ThinQTT.SERVICE_PHASE,
        app_level: Header("x-thinq-app-level") = ThinQTT.APP_LEVEL,
        app_os: Header("x-thinq-app-os") = ThinQTT.APP_OS,
        app_type: Header("x-thinq-app-type") = ThinQTT.APP_TYPE,
        app_version: Header("x-thinq-app-ver") = ThinQTT.APP_VERSION,
        message_id: Header("x-message-id") = ThinQMessageID(),
        **kwargs
    ):

        super().__init__(base_url=self.base_url, **kwargs)
