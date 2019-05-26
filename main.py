# make sure that the password is not too short
# otherwise, an OSError occurs while setting up a wi-fi access point
ACCESS_POINT_SSID = 'esp8266-watering'
ACCESS_POINT_PASSWORD = 'helloesp8266'

HTTP_RESPONSE = b"""\
HTTP/1.0 200 OK
Content-Length: %d

%s
"""

HTTP_REDIRECT = b"""\
HTTP/1.0 301 Moved Permanently
Location: /

"""

# HTML form for settings
FORM_TEMPLATE = """\
<html>
    <head>
        <title>Watering system configuration</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h2 style="font-size:10vw">Watering system configuration</h2>
        <h3 style="font-size:5vw">Wi-Fi settings</h3>
        <div style="width: 100%;">
            <form method="post">
                <p style="width: 100%;">SSID:&nbsp;<input name="ssid" type="text" value="%ssid%"/></p>
                <p style="width: 100%;">Password:&nbsp;<input name="pass" type="password"/></p>
                <p style="width: 100%;"><input type="submit" value="Update"></p>
            </form>
        </div>
        <h3 style="font-size:5vw">Watering settings</h3>
        <div style="width: 100%;">
            <form method="post">
                <p style="width: 100%;">Interval:&nbsp;<input name="watering_interval" type="text" value="%watering_interval%"/></p>
                <p style="width: 100%;">Duration:&nbsp;<input name="watering_duration" type="text" value="%watering_duration%"/></p>
                <p style="width: 100%;"><input type="submit" value="Update"></p>
            </form>
        </div>
        <h3 style="font-size:5vw">Measurement settings</h3>
        <div style="width: 100%;">
            <form method="post">
                <p style="width: 100%;">Interval:&nbsp;<input name="measurement_interval" type="text" value="%measurement_interval%"/></p>
                <p style="width: 100%;"><input type="submit" value="Update"></p>
            </form>
        </div>
    </body>
</html>
"""

# returns an HTTP response with a form
def get_form(config):
    form = FORM_TEMPLATE
    form = form.replace('%ssid%', str(config.get('ssid')))
    form = form.replace('%watering_interval%', str(config.get('watering_interval')))
    form = form.replace('%watering_duration%', str(config.get('watering_duration')))
    form = form.replace('%measurement_interval%', str(config.get('measurement_interval')))
    return HTTP_RESPONSE % (len(form), form)

class ConnectionHandler:

    def __init__(self, config):
        self.config = config

    def handle(self, client_s, status_line, headers, data):
        if status_line.startswith('POST') and data:
            # process data from the web forms
            params = data.split('&')
            for param in params:
                parts = param.split('=')
                name = parts[0]
                value = parts[1]
                if name == 'ssid':
                    config.set('ssid', value)
                if name == 'pass':
                    config.set('password', value)
                if name == 'watering_interval':
                    config.set('watering_interval', value)
                if name == 'watering_duration':
                    config.set('watering_duration', value)
                if name == 'measurement_interval':
                    config.set('measurement_interval', value)

            config.store()
            client_s.write(HTTP_REDIRECT)
        else:
            # otherwise, print out html form
            client_s.write(get_form(config))

# returns true if config mode enabled
def is_config_mode(config):
    import util
    return util.is_switch_on(config.get('config_mode_switch_pin'))


# entry point
from weather import Weather
from pump import Pumps
from config import Config
import util

config = Config('main.conf')
pumps = Pumps(config.get('first_pump_pin'), config.get('second_pump_pin'),
              config.get('pump_switch_pin'),
              config.get('watering_interval'), config.get('watering_duration'))
weather = Weather(config.get('dht22_pin'), config.get('measurement_interval'))

# check if we're in configuration mode
if is_config_mode(config):
    from http import HttpServer
    print('enabled configuration mode')
    access_point = util.start_access_point(ACCESS_POINT_SSID, ACCESS_POINT_PASSWORD)
    handler = ConnectionHandler(config)
    ip = access_point.ifconfig()[0]
    HttpServer(ip, 80, handler).start()
    util.reboot()

# main loop
util.connect_to_wifi(config.get('ssid'), config.get('password'))
while True:
    weather.check()
    pumps.check()
    time.sleep(5) # in seconds
