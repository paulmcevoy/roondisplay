import os
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
width = 128
height = 64

from roonapi import RoonApi

appinfo = {
    "extension_id": "python_roon_display",
    "display_name": "Python library for Roon",
    "display_version": "1.0.0",
    "publisher": "gregd",
    "email": "mygreat@emailaddress.com",
}

try:
    core_id = open("/home/pi/roondisplay/my_core_id_file").read()
    token = open("/home/pi/roondisplay/my_token_file").read()
except OSError:
    print("Please authorise first using discovery.py")
    exit()

hostname = "192.168.0.86"

def check_ping():
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False

    return pingstatus

while not check_ping():
    time.sleep(2)
    print(f'Waiting for ping response from {hostname}')



while True:
    try:
        discover = RoonDiscovery(core_id)
        server = discover.first()
        print(discover, server)
        discover.stop()
        print(f'token: {token} server0 {server[0]} server1 {server[1]}')
        roonapi = RoonApi(appinfo, token, server[0], server[1], True)
        break
    except:
        print("Roon Core not up")
        time.sleep(2)
        pass

font = ImageFont.truetype("Quicksand-Regular.ttf", 12)


def get_horz(val,draw):
    w,h = draw.textsize(val,font=font)
    x = (width-w)/2

    return x,0

def print_stuff(draw,val,offset):
        #if the length is greater than 20 then call twice
        if len(val)>20:
            x,y = get_horz(val[:18],draw)
            draw.text((x,y+offset), val[:19], font=font,fill="white")
            x,y = get_horz(val[19:38],draw)
            draw.text((x,y+14+offset), val[19:38], font=font,fill="white")
        else:
            x,y = get_horz(val,draw)
            draw.text((x,y+10+offset), val, font=font,fill="white")

good_list = ["Piboto-Light.ttf", "Quicksand-Regular.ttf", "LiberationSans-Regular.ttf", "LiberationSans-Regular.ttf", "URWGothic-Book.otf", "NimbusMonoPS-Bold.otf", "NimbusSans-Regular.otf"]

def draw_text(track,artist,album):
    with canvas(device) as draw:

        print_stuff(draw,track,0)
        print_stuff(draw,artist,32)
        time.sleep(1)

print("Got token, starting callback")

def my_state_callback(event, changed_ids):
    """Call when something changes in roon."""
    print("my_state_callback event:%s changed_ids: %s" % (event, changed_ids))
    for zone_id in changed_ids:
        try:
            zone = roonapi.zones[zone_id]
            if zone['display_name'] == 'D10s':
                if 'now_playing' in zone.keys():
                    track = zone['now_playing']['three_line']['line1']
                    artist = zone['now_playing']['three_line']['line2']
                    album = zone['now_playing']['three_line']['line3']
                    draw_text(track,artist,album)
                else:
                    draw_text('It\'s full', 'of stars...',' ')

            time.sleep(1)
        except Exception as e:
            print(f'Exception Will Robinson {e}')
#wait_for_connection()
draw_text('My god, it\'s full', 'of stars...',' ')
roonapi.register_state_callback(my_state_callback)

while True:
    time.sleep(1)


time.sleep(2)

