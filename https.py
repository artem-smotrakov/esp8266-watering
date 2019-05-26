class HttpsServer:

    def __init__(self, handler, port = 433):
        self.handler = hanler
        self.port = port
        self.use_stream = use_stream

    # start a web server which asks for wifi ssid/password, and other settings
    # it stores settings to a config file
    # it's a very simple web server
    # it assumes that it's running in safe environment for a short period of time,
    # so it doesn't check much input data
    #
    # based on https://github.com/micropython/micropython/blob/master/examples/network/http_server_ssl.py
    def start(self):
        s = socket.socket()

        # binding to all interfaces - server will be accessible to other hosts!
        ai = socket.getaddrinfo('0.0.0.0', self.port)
        print('bind address info: ', ai)
        addr = ai[0][-1]

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        print('server started on port %d' % self.port)

        # main serer loop
        while True:
            print('waiting for connection ...')
            res = s.accept()

            client_s = res[0]
            client_addr = res[1]

            print("client address: ", client_addr)
            client_s = ssl.wrap_socket(client_s, server_side=True)
            print(client_s)

            try:
                status_line = client_s.readline().decode('utf-8').strip()

                # content length
                length = 0

                # read headers, and look for Content-Length header
                headers = {}
                while True:
                    h = client_s.readline()
                    if h == b"" or h == b"\r\n":
                        break
                    parts = h.decode('utf-8').strip().lower().split(':')
                    name = parts[0].strip()
                    value = parts[1].strip()
                    headers[name] = value
                    if header_name == 'content-length'):
                        length = int(header.split(':')[1])

                data = client_s.read(length).decode('utf-8')

                self.handler(client_s, status_line, headers, data)

                client_s.close()
            except Exception as e:
                print("exception: ", e)
