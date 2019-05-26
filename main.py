try:
    import usocket as socket
except:
    import socket
import ussl as ssl

# even if TLS is used here, MicroPython for ESP8260 doesn't support
# certificate validation
# we're relatively safe if an attacker can only eavesdrop
# because all data should be encrypted
# but if the attacker can modify the trafic, then we're in a trouble
# since the attacker can implement a man-in-the-middle attack

HTTP_RESPONSE = b"""\
HTTP/1.0 200 OK
Content-Length: %d

%s
"""

HTTP_REDIRECT = b"""\
HTTP/1.0 200 OK
Location: /


"""

# HTML form for settings
FORM = b"""\
<html>
    <head>
        <title>Watering system configuration</title>
    </head>
    <body>
        <h2>Watering system configuration</h2>
        <h3>Wi-Fi settings</h3>
        <div>
            <form method="post">
                <p>SSID:&nbsp;<input name="ssid" type="text"/></p>
                <p>Password:&nbsp;<input name="pass" type="password"/></p>
                <p><input type="submit" value="Update"></p>
            </form>
        </div>
    </body>
</html>
"""

CONFIG = 'main.conf'
SERVER_PORT = 443
INDENT = '    '

# make sure that the password is not too short
# otherwise, an OSError occurs while setting up a wi-fi access point
ACCESS_POINT_SSID = 'esp8266-watering'
ACCESS_POINT_PASSWORD = 'helloesp8266'

DELAY = 5
REBOOT_DELAY = 5

# returns an HTTP response with a form
def get_form():
    return HTTP_RESPONSE % (len(FORM), FORM)

# reboot the board after some delay
def reboot():
    import time
    import machine
    print('rebooting ...')
    time.sleep(REBOOT_DELAY)
    machine.reset()

# start a web server which asks for wifi ssid/password, and other settings
# it stores settings to a config file
# it's a very simple web server
# it assumes that it's running in safe environment for a short period of time,
# so it doesn't check much input data
#
# based on https://github.com/micropython/micropython/blob/master/examples/network/http_server_ssl.py
def start_local_server(use_stream = True):
    s = socket.socket()

    # binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo('0.0.0.0', SERVER_PORT)
    print('bind address info: ', ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print('server started on https://192.168.4.1:%d/' % SERVER_PORT)

    # main serer loop
    while True:
        print('waiting for connection ...')
        res = s.accept()

        client_s = res[0]
        client_addr = res[1]

        print("client address: ", client_addr)
        client_s = ssl.wrap_socket(client_s, server_side=True)
        print(client_s)

        print("client request:")
        if use_stream:
            # both CPython and MicroPython SSLSocket objects support read() and
            # write() methods
            #
            # browsers are prone to terminate SSL connection abruptly if they
            # see unknown certificate, etc.
            # we must continue in such case -
            # next request they issue will likely be more well-behaving and
            # will succeed
            try:
                req = client_s.readline().decode('utf-8').strip()
                print(INDENT + req)

                # content length
                length = 0

                # read headers, and look for Content-Length header
                while True:
                    h = client_s.readline()
                    if h == b"" or h == b"\r\n":
                        break
                    header = h.decode('utf-8').strip().lower()
                    if header.startswith('content-length'):
                        length = int(header.split(':')[1])
                    print(INDENT + header)

                if req.startswith('POST') and length > 0:
                    # process data from the web form
                    data = client_s.read(length).decode('utf-8')
                    if data:
                        values = read_config()
                        params = data.split('&')
                        for param in params:
                            if param.startswith('ssid='):
                                config['ssid'] = param.split('=')[1]
                            if param.startswith('pass='):
                                config['password'] = param.split('=')[1]

                        write_config(values)
                        client_s.write(HTTP_REDIRECT)
                else:
                    # otherwise, print out html form
                    client_s.write(get_form())

                client_s.close()
            except Exception as e:
                print("exception: ", e)
        else:
            print(client_s.recv(4096))
            client_s.send(get_form())

        # close the connection
        client_s.close()

def write_config(values):
    import ujson
    f = open(CONFIG, 'w')
    f.write(ujson.dump(values))
    f.close()

# read config from a file
def read_config():
    import os
    if not CONFIG in os.listdir():
        print('cannot find ' + CONFIG)
        return {}
    import ujson
    f = open(CONFIG)
    config = ujson.load(f)
    f.close()
    return config

# start wifi access point
def start_access_point():
    import network
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ACCESS_POINT_SSID, password=ACCESS_POINT_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)

# read ssid/password from a file, and try to connect
# returns true in case of successful connection
def connect_to_wifi(config):
    if not config:
        print('config is empty')
        return

    if not config['ssid'] or not config['password']:
        print('could not find ssid/password in config file')
        return False

    # try to connect
    import network
    import time
    print('connecting to network: %s' % ssid)
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.connect(config['ssid'], config['password'])

    # wait some time
    attempt = 0
    while attempt < 11 and not nic.isconnected():
        print('connecting ...')
        time.sleep(1.0)
        attempt = attempt + 1

    if nic.isconnected():
        print('connected')
        return True
    else:
        print('connection failed')
        return False

# returns true if a switch on the specified pin is on
def is_switch_on(pin_number):
    from machine import Pin
    pin = Pin(pin_number, Pin.IN)
    return True if pin.value() == 1 else False

# returns true if config mode enabled
def is_config_mode(config):
    return is_switch_on(config['config_mode_switch_pin'])


# entry point

from weather import Weather
from pump import Pumps

config = read_config()
print('configuration: %s' % config)

pumps = Pumps(config['first_pump_pin'], config['second_pump_pin'], config['pump_switch_pin'])
weather = Weather(config['dht22_pin'], config['measurement_interval'])

# check if we're in configuration mode
if is_config_mode(config):
    print('enabled configuration mode')
    start_access_point()
    start_local_server()
    reboot()
else:
    connect_to_wifi(config)
    while True:
        weather.check()
        pumps.check()
        time.sleep(DELAY)
