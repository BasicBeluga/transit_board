import signal
import sys
import datetime
from dateutil import tz

from gtfs import GTFS
from updater import get_known_feeds, get_latest_feed, get_downloaded_feeds, pull_gtfs_rt_feeds, get_closest_feeds

# Hide Exit Exception
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

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
            (40, urwid.Text(('normal', gtfs.trips.find_by_id(self.trip_id)['trip_headsign']), align='left')),
            (9, urwid.Text(('normal', self.route_number), align='left')),
            (8, urwid.Text((exp_text_color, nice_datetime(self.expected)), align='left')),
        ])
        return columns


sysargs = sys.argv


pull_gtfs_rt_feeds()

get_closest_feeds(5)

quit()
if '-u' in sysargs:
    for feed in get_known_feeds():
        get_latest_feed(feed)

if '-t' in sysargs:
    transit_system = sysargs[sysargs.index('-t') + 1]
    if '-s' in sysargs:
        stop_id = sysargs[sysargs.index('-s') + 1]
    else:
        stop_id = None
else:
    transit_system = 'hfx'
    stop_id = '8695'

available_feeds = get_downloaded_feeds()

if transit_system in available_feeds:
    gtfs_dir = available_feeds[transit_system]
elif transit_system == 'hfx':
    gtfs_dir = "./route_files/CA_NS_HALIFAX/"
elif transit_system == 'bart':
    gtfs_dir = "./route_files/US_CA_SF/"

gtfs = GTFS(gtfs_dir)
if stop_id is not None:
    stop = gtfs.stops.find_by_id(stop_id)
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

for row in gtfs.real_time.get_stop_data(stop_id):
    rows.append(TransitRow(**row).gen_transit_row())

pile = urwid.Pile(rows)
map1 = urwid.AttrMap(pile, 'normal')
fill = urwid.Filler(map1)
map2 = urwid.AttrMap(fill, 'normal')
loop = urwid.MainLoop(map2, palette, unhandled_input=exit_on_q)
loop.screen.set_terminal_properties(colors=256)
loop.run()

