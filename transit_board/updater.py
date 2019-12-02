import zipfile
import requests
import os
import io
import json


def get_known_feeds():
    feeds = []
    PATH = './route_links/'
    for file in os.listdir(PATH):
        feeds.append(PATH + file)
    return feeds


def get_latest_feed(filename):
    with open(filename, 'r') as f:
        name = f.name.split('/')[-1].split('.')[0]
        j = json.load(f)
        static = j['static']
        dynamic = j['dynamic']

    r = requests.get(static)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('./static_route_data/' + name + '/')

    with open('./static_route_data/' + name + '/real_time_link.txt', 'w') as f:
        f.write(dynamic)

def get_downloaded_feeds():
    feeds = {}
    PATH = './static_route_data/'
    for file in os.listdir(PATH):
        feeds[file] = PATH + file + "/"

    return feeds

def make_required_directories():
    pass