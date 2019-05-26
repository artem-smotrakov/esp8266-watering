CONFIG = 'main.conf'

# make sure that the password is not too short
# otherwise, an OSError occurs while setting up a wi-fi access point
ACCESS_POINT_SSID = 'esp8266-watering'
ACCESS_POINT_PASSWORD = 'helloesp8266'

DELAY = 5

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

# returns an HTTP response with a form
def get_form():
    return HTTP_RESPONSE % (len(FORM), FORM)

def connection_handler(client_s, status_line, headers, data):
    if status_line.startswith('POST') and data:
        # process data from the web forms
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

# returns true if config mode enabled
def is_config_mode(config):
    import util
    return util.is_switch_on(config['config_mode_switch_pin'])


# entry point
from weather import Weather
from pump import Pumps
import util

config = read_config()
print('configuration: %s' % config)

pumps = Pumps(config['first_pump_pin'], config['second_pump_pin'], config['pump_switch_pin'])
weather = Weather(config['dht22_pin'], config['measurement_interval'])

# check if we're in configuration mode
if is_config_mode(config):
    import HttpsServer from https
    print('enabled configuration mode')
    util.start_access_point(ACCESS_POINT_SSID, ACCESS_POINT_PASSWORD)
    HttpServer(connection_handler).start()
    util.reboot()

# main loop
connect_to_wifi(config['ssid'], config['password'])
while True:
    weather.check()
    pumps.check()
    time.sleep(DELAY)
