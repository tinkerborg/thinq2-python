from marshmallow_dataclass import dataclass

from thinqtt.model.gateway import Gateway
from thinqtt.schema import BaseSchema


@dataclass(base_schema=BaseSchema)
class OAuthToken:
    access_token: str
    expires_in: str
    refresh_token: str = None

    def update(self, token: "OAuthToken"):
        self.access_token = token.access_token
        self.expires_in = token.expires_in


@dataclass
class UserProfile:
    user_id: str
    user_no: str


@dataclass
class ThinQTTSession:
    country_code: str
    language_code: str
    client_id: str
    gateway: Gateway
    profile: UserProfile = None
    token: OAuthToken = None
