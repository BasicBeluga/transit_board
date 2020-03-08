import zipfile
import requests
import os
import io
import json
from location import get_location
from haversine import haversine

PATH = './static_route_data/'

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

    if not os.path.exists(PATH):
        os.mkdir(PATH)

    for file in os.listdir(PATH):
        feeds[file] = PATH + file + "/"

    return feeds

def make_required_directories():
    os.mkdir(PATH)


def pull_gtfs_rt_feeds():
    page_no = 1
    pages = 10000
    feed_data = []
    while page_no <= pages:
        r = requests.get(
            "https://api.transitfeeds.com/v1/getFeeds",
            params={
                'key': '8f5eb6b0-f46d-4f75-af73-66ebac29499a',
                'limit': 100,
                # 'type': 'gtfsrealtime',
                'page': page_no
            }
        )
        r_json = r.json()
        pages = r_json['results']['numPages']
        feed_data += r_json['results']['feeds']
        page_no+=1

    return feed_data

def get_closest_feeds(number_of_feeds=1, max_distance=300):
    pt, fuzz = get_location().h_rep()
    feed_data = pull_gtfs_rt_feeds()

    distances = []

    for feed in feed_data:
        feed_pos = (feed['l']['lat'], feed['l']['lng'])
        distance = haversine(pt, feed_pos) - (fuzz/1000)
        distances += [distance]

    feeds = sorted(zip(distances, feed_data), key=lambda x: x[0]) #[:number_of_feeds]

    for idx, feed in enumerate(feeds):
        if feed[0] > max_distance:
            feeds = feeds[:idx]
            break

    for feed in feeds:
        print(feed)

