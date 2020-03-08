import signal
import sys
import datetime
from dateutil import tz

from gtfs import GTFS
from updater import get_known_feeds, get_latest_feed, get_downloaded_feeds, pull_gtfs_rt_feeds, get_closest_feeds
from wizard import Wizard

# Hide Exit Exception
# signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

import urwid

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def nice_datetime(in_time):
    return in_time.astimezone(to_zone).strftime("%H:%M")

def dict_2_palette(in_dict):
    # name, foreground, background, mono, foreground_high, background_high
    out_list = []
    out_list.append(in_dict['name'])
    out_list.append(in_dict['foreground'])
    out_list.append(in_dict['background'])
    if 'mono' in in_dict:
        out_list.append(in_dict['mono'])
        if 'foreground_high' in in_dict:
            out_list.append(in_dict['foreground_high'])
            if 'background_high' in in_dict:
                out_list.append(in_dict['background_high'])

    return tuple(out_list)


palette = [
    dict_2_palette({
        'name': 'normal',
        'foreground': 'black',
        'background': 'white',
        'mono': '',
        # 'foreground_high': '',
        # 'background_high': '#000'
    }),
    dict_2_palette({
        'name': 'bold',
        'foreground': 'white',
        'background': 'black',
        'mono': '',
        # 'foreground_high': '#fc2,bold',
        # 'background_high': '#000,bold'
    }),
    dict_2_palette({
        'name': 'good_green',
        'foreground': 'black',
        'background': 'light green',
        'mono': '',
        # 'foreground_high': '#fc2,bold',
        # 'background_high': '#000,bold'
    }),
    dict_2_palette({
        'name': 'delayed_yellow',
        'foreground': 'black',
        'background': 'yellow',
        'mono': '',
        # 'foreground_high': '#fc2,bold',
        # 'background_high': '#000,bold'
    }),
    dict_2_palette({
        'name': 'bad_red',
        'foreground': 'white',
        'background': 'light red',
        'mono': '',
        # 'foreground_high': '#fc2,bold',
        # 'background_high': '#000,bold'
    }),
]

class TransitRow():
    def __init__(self, **kwargs):
        self.time = datetime.datetime.now()
        self.destination = 'destination'
        self.platform = '1'
        self.expected_msg = 'delayed'
        self.expected = datetime.datetime.now()
        self.route_number = ''
        for key, value in kwargs.items():
            setattr(self, key, value)

    def gen_transit_row(self):
        if self.time  >= self.expected - datetime.timedelta(minutes=1):
            exp_text_color = 'good_green'
        elif self.time  >= self.expected - datetime.timedelta(minutes=10):
            exp_text_color = 'delayed_yellow'
        else:
            exp_text_color = 'bad_red'



        columns = urwid.Columns([
            (6, urwid.Text(('normal', nice_datetime(self.time)), align='left')),
            (40, urwid.Text(('normal', self.gtfs.trips.find_by_id(self.trip_id)['trip_headsign']), align='left')),
            (9, urwid.Text(('normal', self.route_number), align='left')),
            (8, urwid.Text((exp_text_color, nice_datetime(self.expected)), align='left')),
        ])
        return columns


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

    rows = [
        urwid.Text(('normal', stop['stop_name']), align='left', ),
        urwid.Columns([
            (6, urwid.Text(('bold', 'TIME'), align='left',)),
            (40, urwid.Text(('bold', 'DESTINATION'), align='left')),
            (9, urwid.Text(('bold', 'PLATFORM'), align='left')),
            (8, urwid.Text(('bold', 'EXPECTED'), align='left')),
        ])
    ]

    for row in gtfs.real_time.get_stop_data(click_args['stop_id']):
        rows.append(TransitRow(gtfs=gtfs, **row).gen_transit_row())

    pile = urwid.Pile(rows)
    map1 = urwid.AttrMap(pile, 'normal')
    fill = urwid.Filler(map1)
    map2 = urwid.AttrMap(fill, 'normal')
    loop = urwid.MainLoop(map2, palette, unhandled_input=exit_on_q)
    loop.screen.set_terminal_properties(colors=256)
    loop.run()

    print('done.')
    exit()

if __name__ == '__main__':
    hello()


# pull_gtfs_rt_feeds()

# get_closest_feeds(5)

# quit()





