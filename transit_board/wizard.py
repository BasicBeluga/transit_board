import urwid
from enum import Enum
from gtfs import GTFS
from local_settings import Settings

class HandlerEnum(Enum):
    NOT_FOUND = -1
    LOCATE_ME = 0
    GOOGLE = 1
    PROMPT = 2
    ENVIROMENT = 3


class Wizard():
    def __init__(self, click_args, available_feeds, update_func):
        self.click_args = click_args
        self.available_feeds = available_feeds
        self.main = None
        self.update_func = update_func
        self.gtfs = None

    def run(self):
        search_option = None
        if not self.click_args.get('transit_system', None):
            stop_finder_strat_msg =  "Welcome to Transit Board. What transit service would you like to use?"
            stop_finder_choices = {
                'Select Downloaded Feed' : "existing",
                # 'Search by Name': "name",
                # 'Search by Location': "location"
            }

            Settings()

            stop_finder_bigchoice = BigChoice(stop_finder_strat_msg, stop_finder_choices)
            loop = urwid.MainLoop(stop_finder_bigchoice.create_element(), palette=[('reversed', 'standout', '')])
            loop.run()
            search_option = stop_finder_bigchoice.choice

        if search_option == "name":
            self.search_by_name()
        elif search_option == "location":
            self.search_by_location()
        elif search_option == "existing":
            transit_system = self.select_downloaded_feed()
            if transit_system == 'update':
                print("Updating...")
                self.update_func()
                transit_system = self.select_downloaded_feed()

            self.click_args = {**self.click_args, 'transit_system': transit_system}

            if self.click_args['transit_system'] in self.available_feeds:
                gtfs_dir = self.available_feeds[self.click_args['transit_system']]
            else:
                print("Bad Stop ID" + click_args['transit_system'])
                exit()
            
        gtfs = GTFS(gtfs_dir)

        if not self.click_args.get('stop_id', None):
            stop_id_msg = "Select a Stop"

            stop_id_choices = dict([(stop['stop_name'], stop['stop_code']) for stop in gtfs.stops.rows])
            stop_id_bigchoice = BigChoice(stop_id_msg, stop_id_choices)
            loop = urwid.MainLoop(stop_id_bigchoice.create_element(), palette=[('reversed', 'standout', '')])
            loop.run()
            self.click_args['stop_id'] = stop_id_bigchoice.choice

        # choice2 = BigChoice(location_provider_prompt, choices)
        # loop = urwid.MainLoop(choice2.create_element(), palette=[('reversed', 'standout', '')])
        # loop.run()
        
        # print(choice1.choice)
        # print(choice2.choice)
        # loop.stop()
        print("Tada!")
        return self.click_args

    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider()]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', self.item_chosen, c)
            body.append(urwid.AttrMap(button, self.run, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(self, button, choice):
        self.exit_program('')
        response = urwid.Text([u'You chose ', choice, u'\n'])
        done = urwid.Button(u'Ok')
        urwid.connect_signal(done, 'click', self.exit_program)
        self.main.original_widget = urwid.Filler(urwid.Pile([response,
            urwid.AttrMap(done, None, focus_map='reversed')]))

    def exit_program(self, button):
        pass

    def search_by_name(self):
        pass

    def search_by_location(self):
        location_provider_prompt = "Please select your location provider."
        location_provider_choices = {
            'locateme (install with brew, macOS only)': HandlerEnum.LOCATE_ME.value, 
            'google location services (alpha)': HandlerEnum.GOOGLE.value, 
            'manual coordinate': HandlerEnum.PROMPT.value, 
            'enviroment coordinate': HandlerEnum.ENVIROMENT.value
        }
        
        location_provider_choice = BigChoice(location_provider_prompt, location_provider_choices)
        loop = urwid.MainLoop(location_provider_choice.create_element(), palette=[('reversed', 'standout', '')])
        loop.run()
    
    def select_downloaded_feed(self):
        feed_select_prompt = "Select your feed provider."
        feed_select_choices = dict(zip(self.available_feeds.keys(),self.available_feeds.keys()))

        feed_select_choice = BigChoice(feed_select_prompt, {**{'UPDATE FROM ROUTE LINKS': 'update'}, **feed_select_choices})
        loop = urwid.MainLoop(feed_select_choice.create_element(), palette=[('reversed', 'standout', '')])
        loop.run()
        return feed_select_choice.choice

        # feef_select_choice.choice = self.click_args.set('transit_system', '')


class BigChoice:
    def __init__(self, title, choices):
        self.title = title
        self.choices = choices
        self.chosen = False
        self.choice = None

    def create_element(self):
        self.main = urwid.Padding(
            self.menu(
                self.title, self.choices
            ), left=2, right=2
        )
        top = urwid.Overlay(self.main, urwid.SolidFill(),
            align='center', width=('relative', 60),
            valign='middle', height=('relative', 60),
            min_width=20, min_height=9
        )
        return top

    def item_chosen(self, button, choice):
        self.choice = choice
        self.chosen = True
        raise urwid.ExitMainLoop()

    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider()]
        for c, value in choices.items():
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', self.item_chosen, value)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))