import secrets
import base64
import uuid
import re
import thinq2

from urllib.parse import urlencode, urljoin, urlparse, parse_qs

from uplink.clients.io import RequestTemplate, transitions
from thinq2.client.oauth import OAuthClient
from thinq2.client.gateway import GatewayClient
from thinq2.model.auth import ThinQSession
from thinq2.schema import controller, initializer


@controller(ThinQSession)
class ThinQAuth(RequestTemplate):
    def __call__(self, request_builder):
        self._ret = request_builder.return_type
        request_builder.add_request_template(self)

    def before_request(self, request):
        self.add_headers(*request)

    def add_headers(self, method, url, extras):
        extras["headers"].update(self.base_headers)
        extras["headers"].update(self.auth_headers)

    def after_response(self, request, response):
        if response.status_code == 400:
            # XXX - thinq auth error - find a cleaner way of handling this
            # this gets raised when the oauth code is expired/invalid
            # XXX - this should also die on repeated 400s for the same request
            # (after token refresh)
            try:
                content = response.json()
                if content.get("resultCode") != "0102":
                    return
            except ValueError:
                pass

            self.refresh_token()
            self.add_headers(*request)
            return transitions.sleep(1)

    # XXX - this should throw exceptions if they fail
    def set_token(self, authorization_code):
        self.token = self.oauth_client.get_token(authorization_code)

    def set_token_from_url(self, url):
        params = parse_qs(urlparse(url).query)
        ## XXX - throw error if no code
        self.set_token(params["code"][0])

    def refresh_token(self):
        self.token.update(self.oauth_client.refresh_token(self.token.refresh_token))

    @property
    def auth_headers(self):
        return {
            "x-emp-token": self.token.access_token,
            "x-user-no": self.profile.user_no,
        }

    @property
    def base_headers(self):
        return {
            "x-client-id": self.client_id,
            "x-country-code": self.country_code,
            "x-language-code": self.language_code,
            "x-message-id": self.message_id,
            "x-api-key": thinq2.API_KEY,
            "x-service-code": thinq2.SERVICE_CODE,
            "x-service-phase": thinq2.SERVICE_PHASE,
            "x-thinq-app-level": thinq2.APP_LEVEL,
            "x-thinq-app-os": thinq2.APP_OS,
            "x-thinq-app-type": thinq2.APP_TYPE,
            "x-thinq-app-ver": thinq2.APP_VERSION,
        }

    @property
    def oauth_login_url(self):
        """ Returns a URL to start the OAuth flow """

        url = urljoin(self.gateway.emp_uri, "spx/login/signIn")
        query = urlencode(
            {
                "country": self.country_code,
                "language": self.language_code,
                "client_id": thinq2.LGE_APP_KEY,
                "svc_list": thinq2.SERVICE_CODE,
                "division": thinq2.DIVISION,
                "show_thirdparty_login": thinq2.THIRD_PARTY_LOGINS,
                "redirect_uri": thinq2.OAUTH_REDIRECT_URI,
                "state": uuid.uuid1().hex,
            }
        )
        return "{}?{}".format(url, query)

    @property
    def oauth_backend_url(self):
        return "https://{}.lgeapi.com".format(self.country_code)

    @property
    def oauth_client(self):
        return OAuthClient(base_url=self.oauth_backend_url)

    @property
    def gateway_client(self):
        return GatewayClient(
            # XXX technically if this was reused the messageid would not change
            headers=self.base_headers,
            client_id=self.client_id,
            country_code=self.country_code,
            language_code=self.language_code,
        )

    @property
    def message_id(self):
        id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("UTF-8")
        return re.sub("=*$", "", id)

    @initializer
    def client_id(self):
        return secrets.token_hex(32)

    @initializer
    def gateway(self):
        return self.gateway_client.get_gateway()

    @initializer
    def profile(self):
        return self.oauth_client.get_profile(self.token.access_token)
