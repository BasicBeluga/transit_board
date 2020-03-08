import signal
import sys
import datetime

from board import Board
from gtfs import GTFS
from updater import get_known_feeds, get_latest_feed, get_downloaded_feeds, pull_gtfs_rt_feeds, get_closest_feeds
from wizard import Wizard


# Hide Exit Exception
# signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

import urwid

sysargs = sys.argv

import click

@click.command()
@click.option('-u', is_flag=True, default=False, help='Flag to update known feed from ./route_links')
@click.option('-t', default=None, help='Transit System to use')
@click.option('-s', default=None, help='Stop ID you wish to query')
def hello(u, t, s):
    click_args = {
        'needs_update': u,
        'transit_system': t,
        'stop_id': s
    }

    if click_args['needs_update']:
        for feed in get_known_feeds():
            get_latest_feed(feed)

    available_feeds = get_downloaded_feeds()

    def update_func():
        for feed in get_known_feeds():
            get_latest_feed(feed)

    wizard = Wizard(click_args, available_feeds, update_func)
    click_args = {**click_args, **wizard.run()}

    gtfs = wizard.gtfs


    if click_args['transit_system'] in available_feeds:
        gtfs_dir = available_feeds[click_args['transit_system']]
    elif click_args['transit_system'] == 'hfx':
        gtfs_dir = "./route_files/CA_NS_HALIFAX/"
    elif click_args['transit_system'] == 'bart':
        gtfs_dir = "./route_files/US_CA_SF/"
    else:
        print("Bad Stop ID" + click_args['transit_system'])
        exit()

    gtfs = GTFS(gtfs_dir)

    if click_args['stop_id'] is not None:
        stop = gtfs.stops.find_by_id(click_args['stop_id'])
    else:
        print('Stop not specified. Some valid Stops are:')
        print(','.join([stop['stop_id'] for stop in gtfs.stops.rows[:100]]))
        exit()

    Board(gtfs, click_args['stop_id']).show()

if __name__ == '__main__':
    hello()


# pull_gtfs_rt_feeds()

# get_closest_feeds(5)

# quit()





