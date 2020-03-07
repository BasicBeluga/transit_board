import csv
from google.transit import gtfs_realtime_pb2
import requests
import datetime

class GTFSList():
    def __init__(self, file):
        self.file = file
        self.rows = []
        with open(self.file) as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                self.rows.append(row)

class GTFSAgency(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'agency.txt')


class GTFSCalendar(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'calendar.txt')


class GTFSCalendarDates(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'calendar_dates.txt')


class GTFSFeedInfo(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'feed_info.txt')

class GTFSRoutes(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'routes.txt')


class GTFSShapes(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'shapes.txt')


class GTFSStopTimes(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'stop_times.txt')


class GTFSStops(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'stops.txt')

    def find_by_id(self, stop_id):
        for stop in self.rows:
            if stop['stop_id'] == stop_id:
                return stop
        return None


class GTFSTrips(GTFSList):
    def __init__(self, directory):
        super().__init__(directory + 'trips.txt')

    def find_by_id(self, trip_id):
        for trip in self.rows:
            if trip['trip_id'] == trip_id:
                return trip
        return {'trip_headsign': 'unknown'}

class GTFSRealtime():
    def __init__(self, directory):
        with open(directory + 'real_time_link.txt', 'r') as f:
            self.url = f.readline().rstrip()

    def get_stop_data(self, stop_id):
        stop_data = []
        feed = gtfs_realtime_pb2.FeedMessage()

        try:
            response = requests.get(self.url)
        except requests.exceptions.ConnectionError:
            print(f"Transit feed could not be reached! (Network Error) {self.url}")
            exit(1)

        feed.ParseFromString(response.content)
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                for stu in entity.trip_update.stop_time_update:
                    if stu.stop_id == str(stop_id):
                        # print(entity.trip_update.trip.route_id, datetime.datetime.fromtimestamp(stu.arrival.time))
                        stop_data.append({
                            'route_number': entity.trip_update.trip.route_id,
                            'trip_id': entity.trip_update.trip.trip_id,
                            'expected': datetime.datetime.fromtimestamp(stu.arrival.time),
                            'time': datetime.datetime.fromtimestamp(stu.arrival.time - stu.arrival.delay)
                        })

        return sorted(stop_data, key=lambda x: x['expected'])


class GTFS():
    def __init__(self, directory):
        self.directory = directory
        self.agency = GTFSAgency(directory)
        self.calendar = GTFSCalendar(directory)
        self.calendar_dates = GTFSCalendarDates(directory)
        self.feed_info = GTFSFeedInfo(directory)
        self.routes = GTFSRoutes(directory)
        self.shapes = GTFSShapes(directory)
        self.stop_times = GTFSStopTimes(directory)
        self.stops = GTFSStops(directory)
        self.trips = GTFSTrips(directory)
        self.real_time = GTFSRealtime(directory)
