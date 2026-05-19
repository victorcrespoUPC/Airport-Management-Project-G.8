import math
import matplotlib.pyplot as plt
import os
from airport import IsSchengenairport, LoadAirports, FindAirport
from airport import IsSchengenairport, LoadAirports, FindAirport

class Aircraft:
    def __init__(self, aircraft_id, airline, origin, time):
        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.time = time


    def get_hour(self):
        """Extract hour from time HH:MM"""
        try:  # Tries to convert the "TimeChain" into integer numbers separated by ":", if it recieves an ERROR, then... (line 18)
            return int(self.time.split(':')[0])
        except ValueError:  # The program executes this order giving a false result (ADDED FOR ROBUSTNESS!!)
            return -1

def is_valid_time(time_str):
    """Check if time format is HH:MM"""
    try:
        h, m = time_str.split(':')
        return 0 <= int(h) < 24 and 0 <= int(m) < 60
    except:
        return False

def LoadArrivals(filename):
    if not os.path.exists(filename):
        return []

    arrivals = []
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    i = 1  # We want to skip the first line of the text file, which is only a title without relevant information.
    while i < len(lines):
        line = lines[i]
        parts = line.split()
        if len(parts) >= 4 and is_valid_time(parts[
                                                 2]):  # We can see that we get each aircraft by the characteristics: ID, time, airline and origin
            a = Aircraft(parts[0], parts[3], parts[1], parts[2])
            arrivals.append(a)
        i = i + 1
    return arrivals

def SaveFlights(aircrafts, filename):
    if len(aircrafts) == 0:
        return -1

    f = open(filename, 'w')
    f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        linia = str(a.aircraft_id) + " " + str(a.origin) + " " + \
                str(a.time) + " " + str(a.airline) + "\n"
        f.write(linia)
        i = i + 1
    f.close()
    return 0

def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        print("Error: No flights loaded.")
        return

    hours = [0] * 24
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        t_parts = a.time.split(':')
        hour = int(t_parts[0])
        if hour >= 0 and hour < 24:
            hours[hour] = hours[hour] + 1
        i = i + 1

    plt.figure()
    plt.bar(range(24), hours, color='skyblue')
    plt.title("Hourly arrival frequency")
    plt.show()

def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        print("Error: No data loaded.")
        return

    # We will not be using a dictionary in the next step, but two separate fillable lists.
    noms_cia = []
    comptadors = []

    i = 0
    while i < len(aircrafts):
        cia = aircrafts[i].airline
        trobat = False
        j = 0  # This part reads every flight and counts them per airline/company, creating a comparative bar graph
        while j < len(noms_cia):
            if noms_cia[j] == cia:
                comptadors[j] = comptadors[j] + 1
                trobat = True
            j = j + 1

        if trobat == False:
            noms_cia.append(cia)
            comptadors.append(1)
        i = i + 1

    plt.figure(figsize=(70, 6))  # It needs to be this big! Otherwise we can't read any value
    plt.bar(noms_cia, comptadors, color='orange')  # Bar graph
    plt.title("Flights per airline")
    plt.show()


def PlotFlightsType(aircrafts):
    if len(aircrafts) == 0:
        print("Error: No hi ha dades per mostrar.")
        return

    schengen = 0
    no_schengen = 0

    # Comprem quants vols són de cada tipus
    i = 0
    while i < len(aircrafts):
        # Mirem l'aeroport d'origen de l'avió
        if IsSchengenairport(aircrafts[i].origin) == True:
            schengen = schengen + 1
        else:
            no_schengen = no_schengen + 1
        i = i + 1

    plt.figure()

    # Primera barra (la de sota): Schenegen
    plt.bar(["Vols"], [schengen], color="green", label="Schengen")

    # Segona barra (la de sobre): Non-Schengen
    # El truc és el paràmetre 'bottom': li diem que comenci on acaba la de schengen
    plt.bar(["Vols"], [no_schengen], bottom=[schengen], color="red", label="Non-Schengen")

    plt.title("Tipus de vols (Stacked Bar)")
    plt.ylabel("Numero de vols")
    plt.legend()  # Això fa que surti el quadre explicatiu dels colors
    plt.show()

# As seen in other versions and class exercises, this part calculates the distance of each route.
def haversine(lat1, lon1, lat2, lon2):
    r = 6371
    p1 = lat1 * (math.pi / 180)
    p2 = lat2 * (math.pi / 180)
    dp = (lat2 - lat1) * (math.pi / 180)
    dl = (lon2 - lon1) * (math.pi / 180)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

def LongDistanceArrivals(aircrafts):
    all_ap = LoadAirports("Airports.txt")
    lebl = FindAirport(all_ap, "LEBL")
    long_dist = []

    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        origin_ap = FindAirport(all_ap, a.origin)
        if origin_ap != None and lebl != None:
            dist = haversine(origin_ap.latitude, origin_ap.longitude, lebl.latitude, lebl.longitude)
            if dist > 2000:
                long_dist.append(a)
        i = i + 1
    return long_dist

def MapFlights(aircrafts,
               only_long=False):  # This will show flight routes in Google Earth, we will see long flights by setting:
    all_ap = LoadAirports("Airports.txt")  # only_long = True (it is False by default)
    lebl = FindAirport(all_ap, "LEBL")
    if lebl == None:
        return

    f = open("flights.kml", "w")
    f.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')  # Standard archive for GEarth

    if only_long == True:
        vols_a_pintar = LongDistanceArrivals(aircrafts)
    else:
        vols_a_pintar = aircrafts

    i = 0
    while i < len(vols_a_pintar):
        a = vols_a_pintar[i]
        origin_ap = FindAirport(all_ap, a.origin)
        if origin_ap != None:
            f.write('<Placemark>\n<LineString><coordinates>\n')
            f.write(str(origin_ap.longitude) + "," + str(origin_ap.latitude) + ",0 ")
            f.write(str(lebl.longitude) + "," + str(lebl.latitude) + ",0\n")
            f.write('</coordinates></LineString>\n</Placemark>\n')
        i = i + 1

    f.write('</Document>\n</kml>')
    f.close()


def LoadDepartures(filename): #Almost the same structure as LoadArrivals (changing the updated class and the file tor read)

    if not os.path.exists(filename):
        return []

    departures = [] #list of all the departures loaded by data (of the file)
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    i = 1  # We want to skip the first line of the text file, which is only a title without relevant information.
    while i < len(lines):
        line = lines[i]
        parts = line.split()
        if len(parts) >= 4 and is_valid_time(parts[2]):  # Looking at the structure of the new file, it shows the data as: Aircraft(ID),Destination, Departure time and Airline
            a = Aircraft(aircraft_id=parts[0],airline=parts[3],origin=None,time=None,destination=parts[1],departure_time=parts[2]) #And we get this result using the file structure + The new None settings
            departures.append(a)
        i = i + 1
    return departures

def MergeMovements(arrivals,departures): #Compatible means that departure > arrival
    if len(arrivals)==0 or len(departures)==0:
        return [],-1
    result=[]   #The structure is similar as reading a text file and getting information by using parts[i], but we do it this way because the files are already loaded in the program

    i=0
    while i<len(arrivals):
        a=arrivals[i]
        j=0
        Found = False
        while j<len(departures):
            d=departures[j]
            if a.aircraft_id==d.aircraft_id and a.time<d.departure_time: #Filtering compatible flights
                a.destination=d.destination
                a.departure_time=d.departure_time #Merge both in the same object in order to fill the fields that were set to None in the beginning (aircraft class) (departure_time and destination)
                result.append(a) #a is now filled
                Found = True
            j+=1
        if not Found:
            result.append(a) #If it doesn't find equals, it adds only arrivals.
        i += 1

    j=0
    while j<len(departures): #Now re-running the departures in order to get the ones that didn't get merged
        d=departures[j]
        Found2=False
        k=0
        while k<len(arrivals):
            if arrivals[k].aircraft_id==d.aircraft_id:
                Found2=True
            k += 1
        if not Found2:
            result.append(d)
        j+=1
    return result

def NightAircraft(aircrafts):
    if len(aircrafts)==0:
        return [],-1 #Error if empty! messagebox.showerror?
    result=[]
    j = 0
    while j < len(aircrafts):  # Now re-running the departures in order to get the ones that didn't get merged
        a = aircrafts[j]
        if a.time==None: #If they only have departure information they are considered night aircraft, that's why we filter it like this
            result.append(a)
        i+=1
    return result

# Test section
if __name__ == "__main__":
    arrivals = LoadArrivals("Arrivals.txt")

    if len(arrivals) > 0:
        print(f"Loaded {len(arrivals)} flights")
        PlotArrivals(arrivals)
        PlotAirlines(arrivals)
        PlotFlightsType(arrivals)

        long_dist = LongDistanceArrivals(arrivals)
        print(f"Long-distance flights: {len(long_dist)}")

        MapFlights(arrivals)
        SaveFlights(arrivals, "saved_arrivals.txt")
    else:
        print("Error: No arrivals loaded")
