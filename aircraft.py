import math
import matplotlib.pyplot as plt
import os
from airport import IsSchengenairport, LoadAirports, FindAirport
from airport import IsSchengenairport, LoadAirports, FindAirport

class Aircraft:
    def __init__(self, aircraft_id, airline, origin, time,destination=None, departure_time=None):
        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.time = time
        self.destination = destination
        self.departure_time = departure_time


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
        if a.time is not None:  # ← AFEGEIX aquesta comprovació
            t_parts = a.time.split(':')
            hour = int(t_parts[0])
            if 0 <= hour < 24:
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

def MapFlights(aircrafts, only_long=False):
    all_ap = LoadAirports("Airports.txt")
    lebl = FindAirport(all_ap, "LEBL")
    if lebl is None:
        return

    f = open("flights.kml", "w")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')

    if only_long:
        vols_a_pintar = LongDistanceArrivals(aircrafts)
    else:
        vols_a_pintar = aircrafts

    i = 0
    while i < len(vols_a_pintar):
        a = vols_a_pintar[i]
        origin_ap = FindAirport(all_ap, a.origin)
        if origin_ap is not None:
            f.write('<Placemark>\n<LineString><coordinates>\n')
            f.write(str(origin_ap.longitude) + "," + str(origin_ap.latitude) + ",0 ")
            f.write(str(lebl.longitude) + "," + str(lebl.latitude) + ",0\n")
            f.write('</coordinates></LineString>\n</Placemark>\n')
        i += 1

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

def MergeMovements(arrivals, departures):
    """
    Combina arrivals i departures pel mateix aircraft_id i temps compatibles
    (arrival < departure). Un avió pot aterrar i sortir més d'un cop al dia.
    Retorna una llista unificada.
    """
    if len(arrivals) == 0 or len(departures) == 0:
        return [], -1

    result = []

    i = 0
    while i < len(arrivals):
        a = arrivals[i]
        matched = False
        j = 0
        while j < len(departures):
            d = departures[j]
            # Mateixa aeronau i temps compatible (sortida > arribada)
            if a.aircraft_id == d.aircraft_id and a.time < d.departure_time:
                # Copiem les dades de sortida a l'objecte d'arribada
                a.destination = d.destination
                a.departure_time = d.departure_time
                matched = True
                # NOTA: no fem break perquè pot aterrar/sortir més d'un cop
            j += 1
        result.append(a)  # Afegim sempre (tingui o no sortida)
        i += 1

    # Ara afegim les sortides que no tenien arribada (avions nocturns)
    j = 0
    while j < len(departures):
        d = departures[j]
        found = False
        k = 0
        while k < len(arrivals):
            if arrivals[k].aircraft_id == d.aircraft_id:
                found = True
            k += 1
        if not found:
            result.append(d)  # Afegim sortida sense arribada (nocturn)
        j += 1

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
        j+=1
    return result

#nova funcionalitat
def DayStatistics(aircrafts):
    """
    Calcula i mostra estadístiques del dia en un gràfic de resum:
    - Hora punta d'arribades
    - Aerolínia més freqüent
    - % vols Schengen vs No-Schengen
    - Total de vols, origins únics, avions nocturns
    """
    if len(aircrafts) == 0:
        print("Error: No flights loaded.")
        return

    # ── 1. Comptem arribades per hora ──
    hours = [0] * 24
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        if a.time is not None:
            try:
                h = int(a.time.split(':')[0])
                if 0 <= h < 24:
                    hours[h] += 1
            except:
                pass
        i += 1

    peak_hour = hours.index(max(hours))
    peak_count = max(hours)

    # ── 2. Aerolínia més freqüent ──
    airline_names = []
    airline_counts = []
    i = 0
    while i < len(aircrafts):
        cia = aircrafts[i].airline
        if cia is not None:
            found = False
            j = 0
            while j < len(airline_names):
                if airline_names[j] == cia:
                    airline_counts[j] += 1
                    found = True
                j += 1
            if not found:
                airline_names.append(cia)
                airline_counts.append(1)
        i += 1

    if airline_counts:
        top_idx = airline_counts.index(max(airline_counts))
        top_airline = airline_names[top_idx]
        top_count = airline_counts[top_idx]
    else:
        top_airline = "N/A"
        top_count = 0

    # ── 3. % Schengen vs No-Schengen ──
    schengen = 0
    no_schengen = 0
    i = 0
    while i < len(aircrafts):
        if aircrafts[i].origin is not None:
            if IsSchengenairport(aircrafts[i].origin):
                schengen += 1
            else:
                no_schengen += 1
        i += 1

    total = schengen + no_schengen
    pct_schengen = round(schengen / total * 100, 1) if total > 0 else 0
    pct_noschengen = round(100 - pct_schengen, 1)

    # ── 4. Origins únics i avions nocturns ──
    origins = []
    night_count = 0
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        if a.time is None:
            night_count += 1
        if a.origin is not None and a.origin not in origins:
            origins.append(a.origin)
        i += 1

    total_flights = len(aircrafts)

    # ── Dibuixem el dashboard ──
    fig = plt.figure(figsize=(14, 8))
    fig.patch.set_facecolor('#f0f4f8')
    plt.suptitle("✈  Daily Flight Statistics — LEBL", fontsize=16,
                 fontweight='bold', y=0.98)

    # Gràfic 1 (esquerra dalt): Arribades per hora
    ax1 = fig.add_subplot(2, 2, 1)
    colors = ['#e74c3c' if h == peak_hour else '#3498db' for h in range(24)]
    ax1.bar(range(24), hours, color=colors)
    ax1.set_title("Arrivals per hour", fontweight='bold')
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Flights")
    ax1.set_xticks(range(0, 24, 2))
    ax1.axvline(x=peak_hour, color='red', linestyle='--', alpha=0.5)
    ax1.text(peak_hour + 0.3, max(hours) * 0.9,
             f"Peak: {peak_hour:02d}h\n({peak_count} flights)",
             color='red', fontsize=8)
    ax1.set_facecolor('#f9f9f9')
    ax1.grid(axis='y', alpha=0.4)

    # Gràfic 2 (dreta dalt): Top 10 aerolínies
    ax2 = fig.add_subplot(2, 2, 2)
    # Ordenem les 10 primeres
    paired = list(zip(airline_counts, airline_names))
    paired.sort(reverse=True)
    top10_counts = [x[0] for x in paired[:10]]
    top10_names = [x[1] for x in paired[:10]]
    bar_colors = ['#e74c3c' if n == top_airline else '#2ecc71' for n in top10_names]
    ax2.barh(top10_names[::-1], top10_counts[::-1], color=bar_colors[::-1])
    ax2.set_title("Top 10 airlines", fontweight='bold')
    ax2.set_xlabel("Flights")
    ax2.set_facecolor('#f9f9f9')
    ax2.grid(axis='x', alpha=0.4)

    # Gràfic 3 (esquerra baix): Pie Schengen
    ax3 = fig.add_subplot(2, 2, 3)
    wedges, texts, autotexts = ax3.pie(
        [schengen, no_schengen],
        labels=[f"Schengen\n{pct_schengen}%", f"Non-Schengen\n{pct_noschengen}%"],
        colors=['#2ecc71', '#e74c3c'],
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    ax3.set_title("Schengen vs Non-Schengen", fontweight='bold')

    # Gràfic 4 (dreta baix): Targetes de resum
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    ax4.set_facecolor('#f9f9f9')

    stats = [
        ("✈  Total flights",       str(total_flights)),
        ("🕐  Peak hour",           f"{peak_hour:02d}:00 ({peak_count} flights)"),
        ("🏆  Top airline",         f"{top_airline} ({top_count} flights)"),
        ("🌍  Unique origins",      str(len(origins))),
        ("🌙  Night aircraft",      str(night_count)),
        ("🟢  Schengen flights",    f"{schengen} ({pct_schengen}%)"),
        ("🔴  Non-Schengen",        f"{no_schengen} ({pct_noschengen}%)"),
    ]

    y_pos = 0.95
    for label, value in stats:
        ax4.text(0.05, y_pos, label, transform=ax4.transAxes,
                 fontsize=10, color='#555555')
        ax4.text(0.6, y_pos, value, transform=ax4.transAxes,
                 fontsize=10, fontweight='bold', color='#2c3e50')
        y_pos -= 0.13

    ax4.set_title("Summary", fontweight='bold')

    plt.tight_layout()
    plt.show()

# Test section
if __name__ == "__main__":
    arrivals = LoadArrivals("Arrivals.txt")
    departures = LoadDepartures("Departures.txt")

    if len(arrivals) > 0:
        print(f"Loaded {len(arrivals)} arrivals")
        PlotArrivals(arrivals)
        PlotAirlines(arrivals)
        PlotFlightsType(arrivals)

        long_dist = LongDistanceArrivals(arrivals)
        print(f"Long-distance flights: {len(long_dist)}")

        MapFlights(arrivals)
        SaveFlights(arrivals, "saved_arrivals.txt")
    else:
        print("Error: No arrivals loaded")

    # Test V4
    if len(departures) > 0:
        print(f"Loaded {len(departures)} departures")

        merged = MergeMovements(arrivals, departures)
        print(f"Merged movements: {len(merged)}")

        night = NightAircraft(merged)
        if isinstance(night, list):
            print(f"Night aircraft: {len(night)}")
        else:
            print("No night aircraft found")
    else:
        print("Error: No departures loaded")
