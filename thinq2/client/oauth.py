import datetime
import hmac
import base64
import hashlib

from urllib.parse import urlencode

from uplink import Consumer, Field
from uplink import headers, form_url_encoded, get, post, response_handler
from uplink.arguments import Header
from uplink.decorators import inject
from uplink.hooks import RequestAuditor

import thinq2
from thinq2.model.auth import OAuthToken, UserProfile

REDIRECT_URI = "https://kr.m.lgaccount.com/login/iabClose"


def lg_oauth_signer(request_builder):
    url = "/{}".format(request_builder.relative_url)

    if request_builder.info["data"]:
        # LG expects the form vars to be sorted alphabetically before signing
        form = urlencode(sorted(request_builder.info["data"].items()))
        url = "{}?{}".format(url, form)

    timestamp = datetime.datetime.utcnow().strftime(thinq2.OAUTH_TIMESTAMP_FORMAT)
    message = "{}\n{}".format(url, timestamp).encode("utf8")
    secret = thinq2.OAUTH_SECRET.encode("utf8")
    digest = hmac.new(secret, message, hashlib.sha1).digest()
    signature = base64.b64encode(digest)

    request_builder.info["headers"].update(
        {
            "x-lge-oauth-signature": signature,
            "x-lge-oauth-date": timestamp,
            "x-lge-appkey": thinq2.LGE_APP_KEY,
        }
    )


class BearerToken(Header):
    def _modify_request(self, request_builder, value):
        """Updates request header contents."""
        request_builder.info["headers"]["Authorization"] = "Bearer {}".format(value)


@inject(RequestAuditor(lg_oauth_signer))
@headers({"Accept": "application/json"})
class OAuthClient(Consumer):
    """LG ThinQ OAuth Client"""

    auth = {}

    @form_url_encoded
    @post("oauth/1.0/oauth2/token")
    def get_token(
        self,
        code: Field,
        grant_type: Field = "authorization_code",
        redirect_uri: Field = REDIRECT_URI,
    ) -> OAuthToken.Schema():

        """Retrieves initial OAuth token from authorization code"""

    @form_url_encoded
    @post("oauth/1.0/oauth2/token")
    def refresh_token(
        self, refresh_token: Field, grant_type: Field = "refresh_token"
    ) -> OAuthToken.Schema():

        """Retrieves updated OAuth token from refresh token"""

    @response_handler(lambda response: response.json().get("account"))
    @get("oauth/1.0/users/profile")
    def get_profile(self, access_code: BearerToken) -> UserProfile.Schema:

        """Retrieves current user's OAuth profile"""
