# from dataclasses import dataclass
import requests
from wizard import HandlerEnum

# @dataclass
class FuzzyCoordinate:
    lat: float
    lng: float
    fuzzy_m: float = 0

    def h_rep(self):
        return (self.lat, self.lng), self.fuzzy_m

class LocationHandler():
    def __init__(self):
        pass

    def get_location(self):
        raise Exception("abstraction error")

class LocateMeLocationHandler():
    def __init__(self):
        pass

    def get_location(self):
        result = subprocess.run(['locateme', '-f', '"{LAT},{LON}|{HAC}"'], stdout=subprocess.PIPE)
        return self.parse_cmd_output(result.stdout)

    def parse_cmd_output(self, output: bytes):
        pos_str, fuzzy_m_str = str(output).split('|')
        fuzzy_m = float(fuzzy_m_str[:3])
        lat, lng = [float(''.join([c for c in x if c in '1234567890.-'])) for x in pos_str.split(",")]

        f_coord = FuzzyCoordinate(lat, lng, fuzzy_m)
        return f_coord

class GoogleLocationHandler():
    def __init__(self):
        self.google_key=os.environ.get('GOOGLE_API_TOKEN', None)
        if self.google_key == None:
            raise Exception("No Google API Token Found!")

        
    def get_wifi_points():
        pass
    
    def get_location(self):
        res = requests.post(
            "https://www.googleapis.com/geolocation/v1/geolocate", 
            params={
               'key': self.google_key
            }
        )
        print(res)
        exit()

import os
import platform
import subprocess
from enum import Enum

mode = HandlerEnum.NOT_FOUND

cmd = "where" if platform.system() == "Windows" else "which"
def determine_location_provider():
    try:
        ret_code = subprocess.run([cmd, "locateme"])
        if ret_code == 0:
            mode = HandlerEnum.LOCATE_ME.value
    except:
        pass

    loc_prompt_input = input("Would you like to use Google's Location Services to determine your location (y/N)? ").lower()[:1]
    mode = HandlerEnum.GOOGLE.value if loc_prompt_input == "y" else None

    if mode == HandlerEnum.LOCATE_ME.value:
        handler = LocateMeLocationHandler()
    if mode == HandlerEnum.GOOGLE.value:
        handler = GoogleLocationHandler()

def get_location():
    return handler.get_location()