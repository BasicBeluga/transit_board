from dataclasses import dataclass


@dataclass
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

import os
import platform
import subprocess
from enum import Enum

class HandlerEnum(Enum):
    NOT_FOUND = -1
    LOCATE_ME = 0

mode = HandlerEnum.NOT_FOUND

cmd = "where" if platform.system() == "Windows" else "which"

try:
    subprocess.run([cmd, "locateme"])
    mode = HandlerEnum.LOCATE_ME.value
except:
    pass

if mode == HandlerEnum.LOCATE_ME.value:
    handler = LocateMeLocationHandler()

def get_location():
    return handler.get_location()