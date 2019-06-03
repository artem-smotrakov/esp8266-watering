import ubinascii
import ujson
from rsa import pkcs1

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

    def iss(self, value):
        self.claim['iss'] = value

    def scope(self, value):
        self.claim['scope'] = value

    def iat(self, value):
        self.claim['iat'] = value
        self.claim['exp'] = value + 59 * 60 # 59 minutes, in seconds

    def private_rsa_key(self, key):
        self.key = key

    def build(self):
        encoded_header = ubinascii.b2a_base64(ujson.dumps(self.header))
        encoded_claim = ubinascii.b2a_base64(ujson.dumps(self.claim))
        to_be_signed = '%s.%s' % (encoded_header, encoded_claim)
        signature =pkcs1.sign(to_be_signed, self.key, 'SHA-256')
        encoded_signature = ubinascii.b2a_base64(signature)
        return '%s.%s' % (to_be_signed, encoded_signature)
