try:
    import usocket as _socket
except:
    import _socket

try:
    import ussl as ssl
except:
    import ssl

from http.core import HTTPResponse

# even if SSL/TLS is used here, MicroPython for ESP8260 doesn't support
# validation of server certificate (at least, v1.10)
# so, we're relatively safe if an adversary can just eavesdrop the connection
# because all data should be encrypted
# but if an adversary can modify the trafic, then we're in a trouble
# because server certificate may be replaced in this case

class HttpsClient:

    def __init__(self, request):
        self._request = request

    def connect():
        if not self._request:
            raise Exception('Holy cow! I do not have any HTTP request to send!')
        addr = socket.getaddrinfo(self._request.host(), self._request.port())[0][-1]
        with socket.socket() as s:
            s.connect(addr)
            s = ssl.wrap_socket(s)
            s.write(self._request.build().encode())
            return HTTPResponse.parse(s)
