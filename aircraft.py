import math
import matplotlib.pyplot as plt
import os
from airport import IsSchengenairport, LoadAirports, FindAirport


class Aircraft:
    def __init__(self, aircraft_id, airline, origin, time):
        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.time = time


def LoadArrivals(filename):
    if not os.path.exists(filename):
        return []

    arrivals = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        # Saltem la capçalera si existeix
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4:
                # Validem format de temps hh:mm simple
                if ":" in parts[2] and len(parts[2]) <= 5:
                    a = Aircraft(parts[0], parts[3], parts[1], parts[2])
                    arrivals.append(a)
    return arrivals


def SaveFlights(aircrafts, filename):
    if not aircrafts:
        return -1
    with open(filename, 'w') as f:
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
        for a in aircrafts:
            f.write(f"{a.aircraft_id} {a.origin} {a.time} {a.airline}\n")
    return 0


def PlotArrivals(aircrafts):
    if not aircrafts:
        print("Error: No hi ha vols per mostrar.")
        return

    hours = [0] * 24
    for a in aircrafts:
        hour = int(a.time.split(':')[0])
        if 0 <= hour < 24:
            hours[hour] += 1

    plt.figure()
    plt.bar(range(24), hours, color='skyblue')
    plt.title("Freqüència d'arribades per hora")
    plt.xlabel("Hora del dia")
    plt.ylabel("Número de vols")
    plt.show()


def PlotAirlines(aircrafts):
    if not aircrafts:
        print("Error: No hi ha dades.")
        return

    counts = {}
    for a in aircrafts:
        counts[a.airline] = counts.get(a.airline, 0) + 1

    plt.figure()
    plt.bar(counts.keys(), counts.values(), color='orange')
    plt.title("Vols per companyia")
    plt.show()


def PlotFlightsType(aircrafts):
    if not aircrafts:
        print("Error: No hi ha dades.")
        return

    schengen = 0
    non_schengen = 0
    for a in aircrafts:
        if IsSchengenairport(a.origin):
            schengen += 1
        else:
            non_schengen += 1

    plt.figure()
    plt.bar(["Vols"], [schengen], label="Schengen", color="green")
    plt.bar(["Vols"], [non_schengen], bottom=[schengen], label="Non-Schengen", color="red")
    plt.legend()
    plt.title("Tipus de vols (Schengen vs No-Schengen)")
    plt.show()


def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # Radi de la Terra
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def LongDistanceArrivals(aircrafts):
    # Necessitem la base de dades d'aeroports per saber les coordenades de l'origen
    all_ap = LoadAirports("Airports.txt")
    lebl = FindAirport(all_ap, "LEBL")

    long_dist = []
    for a in aircrafts:
        origin_ap = FindAirport(all_ap, a.origin)
        if origin_ap and lebl:
            dist = haversine(origin_ap.latitude, origin_ap.longitude, lebl.latitude, lebl.longitude)
            if dist > 2000:
                long_dist.append(a)
    return long_dist


def MapFlights(aircrafts, only_long=False):
    all_ap = LoadAirports("Airports.txt")
    lebl = FindAirport(all_ap, "LEBL")
    if not lebl: return

    kml = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'

    # Estils per a les línies
    kml += '<Style id="s_line"><LineStyle><color>ff00ff00</color><width>2</width></LineStyle></Style>'  # Verd
    kml += '<Style id="ns_line"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle></Style>'  # Vermell

    flights_to_show = LongDistanceArrivals(aircrafts) if only_long else aircrafts

    for a in flights_to_show:
        origin_ap = FindAirport(all_ap, a.origin)
        if origin_ap:
            style = "#s_line" if IsSchengenairport(a.origin) else "#ns_line"
            kml += f'<Placemark><styleUrl>{style}</styleUrl><LineString><coordinates>'
            kml += f'{origin_ap.longitude},{origin_ap.latitude},0 {lebl.longitude},{lebl.latitude},0'
            kml += '</coordinates></LineString></Placemark>'

    kml += '</Document></kml>'
    with open("flights.kml", "w") as f:
        f.write(kml)


# Secció de test
if __name__ == "__main__":
    vols = LoadArrivals("arrivals.txt")
    if vols:
        PlotArrivals(vols)
        PlotAirlines(vols)