import requests
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010
import time
from PIL import ImageFont
import random
from roonapi import RoonApi, RoonDiscovery

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1309(serial)

from roonapi import RoonApi

appinfo = {
    "extension_id": "python_roon_display",
    "display_name": "Python library for Roon",
    "display_version": "1.0.0",
    "publisher": "gregd",
    "email": "mygreat@emailaddress.com",
}

discover = RoonDiscovery(None)
servers = discover.all()

print("Shutdown discovery")
discover.stop()

print("Found the following servers")
print(servers)
apis = [RoonApi(appinfo, None, server[0], server[1], False) for server in servers]

auth_api = []
while len(auth_api) == 0:
    print("Waiting for authorisation")
    time.sleep(1)
    auth_api = [api for api in apis if api.token is not None]

api = auth_api[0]

print("Got authorisation")
print(api.host)
print(api.core_name)
print(api.core_id)

print("Shutdown apis")
for api in apis:
    api.stop()

# This is what we need to reconnect
core_id = api.core_id
token = api.token

with open("/home/pi/roondisplay/my_core_id_file", "w") as f:
    f.write(api.core_id)
with open("/home/pi/roondisplay/my_token_file", "w") as f:
    f.write(api.token)


