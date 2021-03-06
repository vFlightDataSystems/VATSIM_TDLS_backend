import libs.lib


class Flightplan:

    def __init__(self, fp):
        self.departure = fp['departure']
        self.arrival = fp['arrival']
        self.flight_rules = fp['flight_rules']
        self.aircraft = fp['aircraft']
        self.aircraft_faa = fp['aircraft_faa']
        self.aircraft_short = fp['aircraft_short']
        self.deptime = fp['deptime']
        self.remarks = fp['remarks']
        self.route = fp['route']
        self.altitude = fp['altitude']
        self.assigned_transponder = fp['assigned_transponder']
        self.revision_id = fp['revision_id']

        self.route = libs.lib.clean_route(self.route, self.departure, self.arrival)

        if not str(self.altitude).isnumeric():
            self.altitude = int(self.altitude[2:] or 0) * 100

        self.amendment = None
        self.amended_route = None
        self.lat = None
        self.lon = None
