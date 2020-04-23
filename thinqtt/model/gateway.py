import uuid
import thinqtt
from urllib import parse
from marshmallow_dataclass import dataclass


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
                "svc_list": thinqtt.SERVICE_CODE,
                "client_id": thinqtt.OAUTH_CLIENT_ID,
                "division": thinqtt.DIVISION,
                "redirect_uri": thinqtt.OAUTH_REDIRECT_URI,
                "state": uuid.uuid1().hex,
                "show_thirdparty_login": thinqtt.THIRD_PARTY_LOGINS,
            }
        )
        return parse.urljoin(
            self.emp_uri, "spx/login/signIn?{query}".format(query=query)
        )
