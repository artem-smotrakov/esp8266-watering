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

    def set_method(self, method):
        self._method = method

    def set_host(self, host):
        self._host = host

    def set_port(self, n):
        self._port = n

    def set_path(self, path):
        self._path = path

    def set_header(self, name, value):
        self._headers[name] = value

    def set_data(self, data):
        self._data = ''
        if isinstance(data, dict):
            for key, value in data.items():
                self._data = self._data + "%s=%s" % (key, value) + "&"
            self._data = self._data.strip("&")
        else:
            self._data = data

    def build(self):
        first_line = "%s %s HTTP/1.0" % (self._method, self._path)
        self._headers['Host'] = "%s:%d" % (self._host, self._port)
        self._headers['Content-Length'] = len(self._data)
        headers = ''
        for key, value in self._headers.items():
            headers = headers + "%s: %s" % (key, value) + "\n"
        return "%s\n%s\n%s" % (first_line, headers, self._data)

class HTTPResponse:

    def __init__(self):
        self._code = None
        self._headers = {}
        self._data = ''

    @classmethod
    def parse(cls, input):
        response = HTTPResponse()

        status_line = input.readline().strip().split()
        response.set_code(int(status_line[1]))

        length = 0
        headers = {}
        while True:
            line = input.readline().decode('ascii').strip()
            if not line:
                break
            i = line.index(' ')
            name = line[0:i].strip()
            value = line[i + 1:].strip()
            headers[name] = value
            if name == 'Content-Length':
                length = int(value)
        response.set_headers(headers)

        if length > 0:
            response.set_data(input.read(length).decode('ascii'))

        return response

    def set_data(self, data):
        self._data = data

    def set_code(self, code):
        self._code = code

    def set_headers(self, headers):
        self._headers = headers

    def data(self):
        return self._data

    def code(self):
        return self._code
