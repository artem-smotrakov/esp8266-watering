try:
    import usocket as socket
except:
    import socket

class HttpServer:

    def __init__(self, ip, port, handler):
        self.ip = ip
        self.port = port
        self.handler = handler

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
        ai = socket.getaddrinfo(self.ip, self.port)
        addr = ai[0][-1]

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        print('server started on %s:%s' % addr)

        # main serer loop
        while True:
            print('waiting for connection ...')
            res = s.accept()
            client_s = res[0]
            print('accepted')

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
                    if name == 'content-length':
                        length = int(value)

                data = client_s.read(length).decode('utf-8')

                self.handler.handle(client_s, status_line, headers, data)

                client_s.close()
            except Exception as e:
                print("exception: ", e)
