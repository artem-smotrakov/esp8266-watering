# ssid and password for the access point
# make sure that the password is not too short
# otherwise, an OSError occurs while setting up a wi-fi access point
ACCESS_POINT_SSID = 'esp8266-watering'
ACCESS_POINT_PASSWORD = 'helloesp8266'

# template for an HTTP response which is sent by the server
HTTP_RESPONSE = b"""\
HTTP/1.0 200 OK
Content-Length: %d

%s
"""

# HTTP redirect response which is sent by the server after processing
# data from the form below
HTTP_REDIRECT = b"""\
HTTP/1.0 301 Moved Permanently
Location: /

"""

# an HTML form for configuring the device
FORM_TEMPLATE = """\
<html>
    <head>
        <title>Watering system configuration</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script type="text/javascript">
            function init() {
                var s = document.getElementById('error_handling_options');
                for (var i = 0; i < s.options.length; i++) {
                    if (s.options[i].value == '%error_handling%') {
                        s.options[i].selected = true;
                    }
                }
            }
        </script>
    </head>
    <body>
        <h2 style="font-size:10vw">Watering system configuration</h2>
        <form method="post">
            <h3 style="font-size:5vw">Wi-Fi settings</h3>
            <div style="width: 100%;">
                <p style="width: 100%;">SSID:&nbsp;<input name="ssid" type="text" value="%ssid%"/></p>
                <p style="width: 100%;">Password:&nbsp;<input name="password" type="password"/></p>
            </div>
            <h3 style="font-size:5vw">Watering settings</h3>
            <div style="width: 100%;">
                <p style="width: 100%;">Interval:&nbsp;<input name="watering_interval" type="text" value="%watering_interval%"/></p>
                <p style="width: 100%;">Duration:&nbsp;<input name="watering_duration" type="text" value="%watering_duration%"/></p>
            </div>
            <h3 style="font-size:5vw">Error handling</h3>
            <div style="width: 100%;">
                <p style="width: 100%;">
                    <select name="error_handling" id="error_handling_options">
                        <option value="stop">Stop</option>
                        <option value="reboot">Reboot</option>
                        <option value="ignore">Ignore</option>
                    </select>
                </p>
            </div>
            <div>
                <p style="width: 100%;"><input type="submit" value="Update"></p>
            </div>
        </form>
    </body>
</html>
"""

# returns an HTTP response with the form above
# the fields in the form contain the current configuration
# (except the password for wi-fi network)
def get_form(config):
    form = FORM_TEMPLATE
    form = form.replace('%ssid%',
                        str(config.get('ssid')))
    form = form.replace('%watering_interval%',
                        str(config.get('watering_interval')))
    form = form.replace('%watering_duration%',
                        str(config.get('watering_duration')))
    form = form.replace('%error_handling%',
                        str(config.get('error_handling')))
    return HTTP_RESPONSE % (len(form), form)

# a handler for incoming HTTP connections
# it prints out the HTML form above,
# and processes the values from the form submitted by a user
# the values are then stored to the configuration
class ConnectionHandler:

    def __init__(self, config):
        self.config = config

    def handle(self, client_s, status_line, headers, data):

        # process data from the web form if a POST request received
        # otherwise, print out the form
        if status_line.startswith('POST') and data:

            # update the config with the data from the form
            params = data.split('&')
            for param in params:
                parts = param.split('=')
                name = parts[0].strip()
                value = parts[1].strip()

                # don't update the password if the password field is empty
                if name == 'password' and not value:
                    continue

                config.set(name, value)

            # store the config
            config.store()

            # redirect the client to avoid resubmitting the form
            client_s.write(HTTP_REDIRECT)
        else:
            client_s.write(get_form(config))


# entry point
from pump import Pumps
from config import Config
from machine import Pin
import util
import time

# load a config from a file
config = Config('main.conf')

# initialize the pumps and the switch which turns them on and off
pumps = Pumps(config.get('first_pump_pin'), config.get('second_pump_pin'),
              config.get('pump_switch_pin'),
              config.get('watering_interval'), config.get('watering_duration'))

# initilize the switch which enables the configuration mode
# if the switch changes its state, then the board is going to reboot immediately
# in order to turn on/off the configuration mode
config_mode_switch = Pin(config.get('config_mode_switch_pin'), Pin.IN)
config_mode_switch.irq(lambda pin: util.reboot())

# first, check if the configuration mode is enabled
# if so, set up an access point, and then start an HTTP server
# the server provides a web form which updates the configuraion of the device
# the server runs on http://192.168.4.1:80
if config_mode_switch.value() == 1:
    from http.server import HttpServer
    print('enabled configuration mode')
    access_point = util.start_access_point(ACCESS_POINT_SSID, ACCESS_POINT_PASSWORD)
    handler = ConnectionHandler(config)
    ip = access_point.ifconfig()[0]
    HttpServer(ip, 80, handler).start()
    util.reboot()

# try to connect to wi-fi if the configuraion mode is disabled
util.connect_to_wifi(config.get('ssid'), config.get('password'))

# then, start the main loop
# in the loop, the board is going to check temperature and humidity
# and also turn on the pumps according to the schedule specified by a user
while True:
    try:
        pumps.check()
    except:
        if config.get('error_handling') == 'reboot':
            util.reboot()
        elif config.get('error_handling') == 'stop':
            raise
        else:
            print('achtung! something wrong happened!')

    time.sleep(1) # in seconds
