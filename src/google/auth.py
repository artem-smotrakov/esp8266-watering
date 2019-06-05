try:
    import ubinascii as binascii
except:
    import binascii

try:
    import ujson as json
except:
    import json

import ntptime
from rsa import pkcs1
from http.core import HTTPRequest
from http.client import HttpsClient

# this class builds a JWT to request an access token
# from the Google OAuth 2.0 Authorization Server using a service account
# see https://developers.google.com/identity/protocols/OAuth2ServiceAccount
class JWTBuilder:

    def __init__(self):
        self.header = {}
        self.header['alg'] = 'RS256'
        self.header['typ'] = 'JWT'
        self.claim = {}
        self.claim['iss'] = ''
        self.claim['scope'] = ''
        self.claim['aud'] = 'https://www.googleapis.com/oauth2/v4/token'
        self.claim['exp'] = 0
        self.claim['iat'] = 0
        self.key = None
        self.expiration = 59 * 60 # 59 minutes, in seconds

    def service_account(self, email):
        self.claim['iss'] = email

    # set a space-delimited list of the permissions
    # that the application requests
    def scope(self, value):
        self.claim['scope'] = value

    # set the time the assertion was issued,
    # specified as seconds since 00:00:00 UTC, January 1, 1970
    def time(self, value):
        self.claim['iat'] = value

    # set an RSA private key for signing a JWT
    def private_rsa_key(self, key):
        self.key = key

    # set the expiration time of the assertion,
    # specified as seconds since 00:00:00 UTC, January 1, 1970
    # this value has a maximum of 1 hour after the issued time
    def expiration(self, time):
        self.expiration = time

    # build a JWT
    def build(self):
        self.claim['exp'] = time + self.expiration
        encoded_header = binascii.b2a_base64(json.dumps(self.header))
        encoded_claim = binascii.b2a_base64(json.dumps(self.claim))
        to_be_signed = '%s.%s' % (encoded_header, encoded_claim)
        signature = pkcs1.sign(to_be_signed, self.key, 'SHA-256')
        encoded_signature = binascii.b2a_base64(signature)
        return '%s.%s' % (to_be_signed, encoded_signature)

class ServiceAccount:

    def __init__(self):
        self.email = ''
        self.scope = ''
        self.key = None

    def email(self, value):
        self.email = email

    def scope(self, value):
        self.scope = scope

    # set an RSA private key for signing a JWT
    def private_rsa_key(self, key):
        self.key = key

    def token(self):

        # prepare a JWT
        builder = JWTBuilder()
        builder.service_account(self.email)
        builder.scope(self.scope)
        builder.private_rsa_key(self.key)
        builder.time(ntptime.time())
        jwt = builder.build()

        # prepare a request
        parameters = {}
        parameters['grant_type'] = 'urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer'
        parameters['assertion'] = jwt
        request = HTTPRequest()
        request.host('www.googleapis.com')
        request.port(443)
        request.path('/oauth2/v4/token')
        request.method('POST')
        request.data(parameters)

        # send the request and extract a token
        response = HttpsClient(request).connect()
        auth_info = json.load(response.data())
        return auth_info['access_token']
