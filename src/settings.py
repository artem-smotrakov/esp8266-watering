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
            <h3 style="font-size:5vw">Measurement settings</h3>
            <div style="width: 100%;">
                <p style="width: 100%;">Interval:&nbsp;<input name="measurement_interval" type="text" value="%measurement_interval%"/></p>
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
    form = form.replace('%ssid%', str(config.get('ssid')))
    form = form.replace('%watering_interval%', str(config.get('watering_interval')))
    form = form.replace('%watering_duration%', str(config.get('watering_duration')))
    form = form.replace('%measurement_interval%', str(config.get('measurement_interval')))
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
