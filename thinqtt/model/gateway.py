import uuid
from thinqtt import ThinQTT
from urllib import parse

from dataclasses import dataclass


@dataclass
class Gateway:
    country_code: str
    language_code: str
    thinq1_uri: str
    thinq2_uri: str
    emp_uri: str

    @property
    def oauth_url(self) -> str:
        query = parse.urlencode(
            {
                "country": self.country_code,
                "language": self.language_code,
                "svc_list": ThinQTT.SERVICE_CODE,
                "client_id": ThinQTT.OAUTH_CLIENT_ID,
                "division": ThinQTT.DIVISION,
                "redirect_uri": ThinQTT.OAUTH_REDIRECT_URI,
                "state": uuid.uuid1().hex,
                "show_thirdparty_login": ThinQTT.THIRD_PARTY_LOGINS,
            }
        )
        return parse.urljoin(
            self.emp_uri, "spx/login/signIn?{query}".format(query=query)
        )
