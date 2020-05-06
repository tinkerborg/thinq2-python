from marshmallow_dataclass import dataclass

from thinq2.model.gateway import Gateway
from thinq2.schema import CamelIDSchema


@dataclass
class OAuthToken:
    access_token: str
    expires_in: str
    oauth2_backend_url: str = None
    refresh_token: str = None

    def update(self, token: "OAuthToken"):
        self.access_token = token.access_token
        self.expires_in = token.expires_in


@dataclass(base_schema=CamelIDSchema)
class UserProfile:
    user_id: str
    user_no: str


@dataclass
class ThinQSession:
    country_code: str
    language_code: str
    client_id: str
    gateway: Gateway
    profile: UserProfile = None
    token: OAuthToken = None
