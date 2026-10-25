import requests
import colorsys
import asyncio
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.controller.mixins.light import LightMixin

class IOT:
    def __init__(self):
        self.clock = Clock("192.168.60.20")

class Clock:
    def __init__(self, ip):
        self.ip = ip
        self.save_state = [4, (255,255,255)]

    #RGB, 1 = color, 3 = breathe, 4 = rainbow
    def set_mode(self, mode, color = (255,255,255)):
        try:
            url = f"http://" + self.ip

            requests.get(url + f'/mode?m={mode}&s=1')

            h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
            h *= 360
            s *= 100
            v *= 100

            for i in range(6):
                requests.get(url + f"/tubecolor?t={i + 1}&h={h}&s={s}&v={v}")

            if not color == (0,0,0):
                self.save_state = [mode, color]
        except:
            print("ENET: Clock failed")
