try:
    import usocket as _socket
except:
    import _socket
try:
    import ussl as ssl
except:
    import ssl

# even if SSL/TLS is used here, MicroPython for ESP8260 doesn't support
# validation of server certificate (at least, v1.10)
# so, we're relatively safe if an adversary can just eavesdrop the connection
# because all data should be encrypted
# but if an adversary can modify the trafic, then we're in a trouble
# because server certificate may be replaced in this case

class HTTPRequest:

    def __init__(self):
        self._method = 'GET'
        self._host = ''
        self._port = 80
        self._path = '/'
        self._headers = {}
        self._data = ''

    def host(self):
        return self._host

    def port(self):
        return self._port

    def method(self, method):
        self._method = method

    def host(self, host):
        self._host = host

    def port(self, n):
        self._port = n

    def path(self, path):
        self._path = path

    def header(self, name, value):
        self._headers[name] = value

    def data(self, data):
        self._data = ''
        if isinstance(data, dict):
            for key, value in data.items():
                self._data = self._data + '%s=%s' % (key, value) + '&'
            self._data = self._data.strip('&')
        else:
            self._data = data

    def build(self):
        first_line = '%s %s HTTP/1.0' % (self._method, self._path)
        headers['Host'] = '%s:%d' % (self._host, self._port)
        headers['Content-Length'] = len(self._data)
        headers = ''
        for key, value in self._headers.items():
            headers = headers + '%s: %s' % (key, value) + '\r\n'
        return '%s \r\n %s \r\n %s' % (first_line, headers, self._data)

class HTTPResponse:

    def __init__(self):
        self._code = None
        self._headers = {}
        self._data = bytes()

    @classmethod
    def parse(cls, input):
        line = input.readline().sprip()
        version, self._code, reason = line.split()
        length = 0
        while True:
            line = input.readline().strip()
            if not line:
                break
            name, value = line.split()
            self._headers[name.strip()] = value.strip()
            if name == 'Content-Length':
                length = int(value)
        if length > 0:
            self._data = input.read(length)

    def data(self):
        return self._data

    def code(self):
        return self._code

class HttpsClient:

    def __init__(sel):
        self._request = None

    def request(self, request):
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
