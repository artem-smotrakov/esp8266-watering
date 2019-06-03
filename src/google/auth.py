import ubinascii
import ujson
from rsa import pkcs1

# this class builds a JWT to request an access token
# from the Google OAuth 2.0 Authorization Server using a service account
# see https://developers.google.com/identity/protocols/OAuth2ServiceAccount
class JWT:

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
    def when(self, time):
        self.claim['iat'] = time

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
        encoded_header = ubinascii.b2a_base64(ujson.dumps(self.header))
        encoded_claim = ubinascii.b2a_base64(ujson.dumps(self.claim))
        to_be_signed = '%s.%s' % (encoded_header, encoded_claim)
        signature = pkcs1.sign(to_be_signed, self.key, 'SHA-256')
        encoded_signature = ubinascii.b2a_base64(signature)
        return '%s.%s' % (to_be_signed, encoded_signature)
