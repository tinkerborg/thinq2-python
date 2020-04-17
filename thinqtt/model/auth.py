from dataclasses import dataclass


@dataclass
class OAuthToken:
    access_token: str
    expires_in: str
    refresh_token: str = None

    def update(self, token: "OAuthToken"):
        self.access_token = token.access_token
        self.expires_in = token.expires_in


@dataclass
class OAuthProfile:
    user_id: str
    user_no: str


@dataclass
class ClientConfig:
    country_code: str = None
    language_code: str = None
