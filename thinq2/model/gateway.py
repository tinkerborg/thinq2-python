import uuid
import thinq2
from urllib import parse
from marshmallow_dataclass import dataclass

from thinq2.schema import CamelCaseSchema


@dataclass(base_schema=CamelCaseSchema)
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
                "svc_list": thinq2.SERVICE_CODE,
                "client_id": thinq2.OAUTH_CLIENT_ID,
                "division": thinq2.DIVISION,
                "redirect_uri": thinq2.OAUTH_REDIRECT_URI,
                "state": uuid.uuid1().hex,
                "show_thirdparty_login": thinq2.THIRD_PARTY_LOGINS,
            }
        )
        return parse.urljoin(
            self.emp_uri, "spx/login/signIn?{query}".format(query=query)
        )
