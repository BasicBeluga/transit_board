
import time
import datetime
from dateutil import tz

import urwid
from util import dict_2_palette

def nice_datetime(in_time):
    return in_time.astimezone(to_zone).strftime("%H:%M")

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

PALETTE = [
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

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

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

class Board():
    def __init__(self, gtfs, stop_id):
        self.gtfs = gtfs
        self.stop_id = stop_id
        self.stop = gtfs.stops.find_by_id(stop_id)
        self.transit_rows = []
        self.last_updated_time = datetime.datetime(1970,1,1)
    
    def show(self):
        gtfs = self.gtfs

        loop = urwid.MainLoop(self.create_view(), PALETTE, unhandled_input=exit_on_q)
        loop.screen.set_terminal_properties(colors=256)
        
        loop.set_alarm_in(1, self.refresh)
        loop.run()

    def refresh(self, loop, data):
        loop.widget = self.create_view()
        loop.set_alarm_in(1, self.refresh)

    def create_view(self):
        transit_row_refresh_required = self.last_updated_time < datetime.datetime.now() - datetime.timedelta(seconds=30)

        self.rows = [
            urwid.Columns([
                (55, urwid.Text(('normal' if not transit_row_refresh_required else 'good_green', self.stop['stop_name']), align='left')),
                (8, urwid.Text(('normal', time.strftime('%H:%M:%S')), align='left'))
            ]),
            urwid.Columns([
                (6, urwid.Text(('bold', ' TIME '), align='left',)),
                (40, urwid.Text(('bold', ' DESTINATION '), align='left')),
                (9, urwid.Text(('bold', 'PLATFORM'), align='left')),
                (8, urwid.Text(('bold', 'EXPECTED'), align='left')),
            ])
        ]

        if transit_row_refresh_required:
            self.last_updated_time = datetime.datetime.now()
            self.transit_rows = []
            for row in self.gtfs.real_time.get_stop_data(self.stop_id):
                self.transit_rows.append(TransitRow(gtfs=self.gtfs, **row).gen_transit_row())

        pile = urwid.Pile(self.rows + self.transit_rows)
        map1 = urwid.AttrMap(pile, 'normal')
        fill = urwid.Filler(map1)
        map2 = urwid.AttrMap(fill, 'normal')

        return map2

