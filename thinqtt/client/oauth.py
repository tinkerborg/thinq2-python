import datetime
import hmac
import base64
import hashlib

from urllib.parse import urlencode

from uplink import Consumer, Field
from uplink import headers, form_url_encoded, get, post, returns
from uplink.arguments import Header
from uplink.decorators import inject
from uplink.hooks import RequestAuditor

import thinqtt
from thinqtt.schema import BaseSchema, EnvelopeResponse
from thinqtt.model.auth import OAuthToken, UserProfile

REDIRECT_URI = "https://kr.m.lgaccount.com/login/iabClose"


def lg_oauth_signer(request_builder):
    # LG expects the form vars to be sorted alphabetically before signing
    url = "/{}".format(request_builder.relative_url)

    if request_builder.info["data"]:
        form = urlencode(sorted(request_builder.info["data"].items()))
        url = "{}?{}".format(url, form)

    timestamp = datetime.datetime.utcnow().strftime(thinqtt.OAUTH_TIMESTAMP_FORMAT)
    message = "{}\n{}".format(url, timestamp).encode("utf8")
    secret = thinqtt.OAUTH_SECRET.encode("utf8")
    digest = hmac.new(secret, message, hashlib.sha1).digest()
    signature = base64.b64encode(digest)

    request_builder.info["headers"].update(
        {
            "x-lge-oauth-signature": signature,
            "x-lge-oauth-date": timestamp,
            "x-lge-appkey": thinqtt.LGE_APP_KEY,
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
    @returns.json
    @post("oauth/1.0/oauth2/token")
    def get_token(
        self,
        code: Field,
        grant_type: Field = "authorization_code",
        redirect_uri: Field = REDIRECT_URI,
    ) -> OAuthToken.Schema:

        """Retrieves initial OAuth token from authorization code"""

    @form_url_encoded
    @returns.json
    @post("oauth/1.0/oauth2/token")
    def refresh_token(
        self, refresh_token: Field, grant_type: Field = "refresh_token"
    ) -> OAuthToken.Schema:

        """Retrieves updated OAuth token from refresh token"""

    @returns.json
    @get("oauth/1.0/users/profile")
    def get_profile(
        self, access_code: BearerToken
    ) -> EnvelopeResponse.wrap(UserProfile, envelope="account"):

        """Retrieves current user's OAuth profile"""
