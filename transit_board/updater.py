import zipfile
import requests
import os
import io
import json
# from location import get_location
from haversine import haversine

PATH = './static_route_data/'
ROUTE_LINKS_PATH = './route_links/'

KEY = '8f5eb6b0-f46d-4f75-af73-66ebac29499a'

def get_known_feeds():
    feeds = []
    for file in os.listdir(ROUTE_LINKS_PATH):
        feeds.append(ROUTE_LINKS_PATH + file)
    return feeds

def create_new_route_link(name, gtfs, vehicle_positions=None, alerts=None, trip_updates=None):
    new_name = '_' + '_'.join(word.strip() for word in reversed(name.split(',')))
    with open(ROUTE_LINKS_PATH + new_name + '.json', 'w') as new_link:
        route_object = {
            'gtfs': gtfs,
            'vehicle_positions': vehicle_positions,
            'alerts': alerts,
            'trip_updates': trip_updates,
            'name': name
        }
        new_link.write(json.dumps(route_object))

def get_latest_feed(filename):
    with open(filename, 'r') as f:
        name = f.name.split('/')[-1].split('.')[0]
        j = json.load(f)
        print(j)
        static = j['gtfs']
        dynamic = j['trip_updates']

    r = requests.get(static)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('./static_route_data/' + name + '/')
    if dynamic:
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
                'key': KEY,
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

def pull_locations():
    locations = requests.get(
        "https://api.transitfeeds.com/v1/getLocations",
        params={
            'key': KEY,
        }
    ).json()['results']['locations']

    return {location['t']: location for location in locations}

def pull_location_detail(location_id):
    page_no = 1
    pages = 10000
    feed_data = []
    while page_no <= pages:
        r = requests.get(
            "https://api.transitfeeds.com/v1/getFeeds",
            params={
                'key': KEY,
                'limit': 100,
                # 'type': 'gtfsrealtime',
                'page': page_no,
                'location': location_id
            }
        )
        r_json = r.json()
        pages = r_json['results']['numPages']
        feed_data += r_json['results']['feeds']
        page_no += 1

    # print(feed_data)
    for feed in feed_data:
        print(feed['t'], feed['u']['d'])

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

