class Gate:
    "Represents an individual boarding gate"
    def __init__(self, name):
        self.name = name
        self.occupied = False      # Boolean: True if an aircraft is at the gate
        self.aircraft_id = None    # Stores the ID of the aircraft (e.g., 'DALEN')

class BoardingArea:
    "Represents a specific area containing a list of gates"
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type      # Schengen or non-Schengen
        self.gates = []            # List of Gate objects

class Terminal:
    "Represents an airport terminal (e.g., T1) with its areas and associated airlines"

    def __init__(self, name):
        self.name = name
        self.boarding_areas = []   # List of BoardingArea objects
        self.airlines = []         # List of airline ICAO codes

class BarcelonaAP:
    "Main class representing the Barcelona Airport (LEBL)"
    def __init__(self, code):
        self.code = code
        self.terminals = []        # List of Terminal objects


def SetGates(area, init_gate, end_gate, prefix):

    # 1. Validation: end_gate must be greater than init_gate
    if end_gate <= init_gate:
        return -1

    # 2. Drop previous list of gates (resetting the list)
    area.gates = []

    gate_num = init_gate

    while gate_num <= end_gate:
        gate_name = f"{prefix}{gate_num}"

        # We create the object Gate i we added to the area
        new_gate = Gate(gate_name)
        area.gates.append(new_gate)

        # INCREMENT MANUAL: passem a la següent porta
        gate_num += 1

    return 0

