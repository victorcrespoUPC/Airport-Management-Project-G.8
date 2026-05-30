import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from airport import *
from aircraft import *
from LEBL import *

# Load all airports from file (for searching coordinates)
all_airports = LoadAirports("Airports.txt")
i = 0
while i < len(all_airports):
    ap = all_airports[i]
    SetSchengen(ap)

    i = i + 1

# This is the list shown in the interface (starts empty)
airports = []


def load_airports():
    global airports
    filename = filedialog.askopenfilename(
        title="Select filed airports",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        airports = LoadAirports(filename) #Load airports from the selected file
        i = 0
        while i < len(airports):
            ap = airports[i]
            SetSchengen(ap)
            i = i + 1
        update_listbox()
        messagebox.showinfo("Correct", f"You loaded {len(airports)} airports.")

#Manually adds a new airport using the ICAO code entered in the UI
def add_airport():
    code = entry_code.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Introduce an ICAO code.")
        return

    # Search in the full database and check if the code exists
    found = FindAirport(all_airports, code)
    if found is None:
        messagebox.showerror("Error", f"Airport {code} not found in database.")
        return

    # If found, Add to the visible list
    SetSchengen(found)
    AddAirport(airports, found)
    update_listbox() #Refresh the UI list display
    entry_code.delete(0, tk.END) #Clear the input text box

#Remove an airport from the active working list with its ICAO code
def remove_airport():
    code = entry_code.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Enter the ICAO code of the airport you want to eliminate.")
        return
    #Remove the airport form the list
    result = RemoveAirport(airports, code)
    if result == -1: #Reason why we needed -1 in prior result!
        messagebox.showerror("Error", f"The airport {code} isn't registered.")
    else:
        messagebox.showinfo("Success", f"Airport {code} was eliminated.")
        update_listbox()
    entry_code.delete(0, tk.END)

#Filters and saves only the Schengen airports from the active list into a new text file
def save_schengen():
    if not airports:
        messagebox.showerror("Error", "No airports were loaded.")
        return
    #We ask the user where they want to save the output file
    filename = filedialog.asksaveasfilename(
        title="Save Schengen airports",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        result = SaveSchengenAirports(airports, filename)
        if result == -1:
            messagebox.showerror("Error", "No Schengen airports found to save.")
        else:
            messagebox.showinfo("Success", "Schengen airports saved successfully.")

#Generates a comparison plot of the currently loaded airports
def show_plot():
    if not airports:
        messagebox.showerror("Error", "No airports were loaded!")
        return
    PlotAirports(airports)
    
#Generates a KML file with the geolocation of the airports to open it with Google Earth
def show_map():
    if not airports:
        messagebox.showerror("Error", "There are no loaded airports.")
        return
    MapAirports(airports)
    messagebox.showinfo("KML created", "File airports.kml was generated.\n Use Google Earth to open it.")

#Clears and refills the Listbox with the updated airport data
def update_listbox():
    listbox.delete(0, tk.END)
    i = 0
    while i < len(airports):
        ap = airports[i]

        if ap.Schengen == True:
            schengen_str = "✔ Schengen"
        else:
            schengen_str = "✘ Not a Schengen airport"

        #This will create the textline adding the necessary parts.
        #We will be aproximating the distance values to 4 decimals (by using round).
        linia = str(ap.code) + " | Latitude: " + str(round(ap.latitude, 4)) + \
                " | Longitude: " + str(round(ap.longitude, 4)) + " | " + schengen_str

        #And it is added to the listbox
        listbox.insert(tk.END, linia) #Tkinter special item

        i = i + 1

flights = [] #list for the active flights

#Loads a list of incoming flights from a file
def load_arrivals_ui():
    global flights
    filename = filedialog.askopenfilename(title="Select Arrivals file", filetypes=[("Text files", "*.txt")])
    if filename:
        flights = LoadArrivals(filename)
        messagebox.showinfo("Success", f"Loaded {len(flights)} flights.")

#Saves the current list of flights into a text file
def save_flights_ui():
    filename = filedialog.asksaveasfilename(title="Save Flights", filetypes=[("Text files", "*.txt")])
    if filename:
        SaveFlights(flights, filename)

#Generates mapping files for flights
def map_flights_ui(long_only=False):
    MapFlights(flights, only_long=long_only)
    messagebox.showinfo("KML", "flights.kml generated!")

def clear_arrivals():
    global flights
    flights = []
    messagebox.showinfo("Success", "All arrivals cleared.")

#Allows loading a different arrivals file
def reload_arrivals_ui():
    global flights
    filename = filedialog.askopenfilename(
        title="Select New Arrivals File",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        flights = LoadArrivals(filename)
        if len(flights) > 0:
            messagebox.showinfo("Success", f"Loaded {len(flights)} new flights.")
        else:
            messagebox.showerror("Error", "No valid flights found in file.")

bcn_airport = None
flights=[]

def load_lebl_structure():
    global bcn_airport
    filename = "Terminals.txt"
    bcn_airport = LoadAirportStructure(filename)
    if bcn_airport:
        messagebox.showinfo("LEBL", "LEBL airport structure loaded correctly.")
    else:
        messagebox.showerror("Error", "Could not find or load Terminals.txt.")


def assign_gates_to_flights():
    global bcn_airport
    if not bcn_airport:
        messagebox.showerror("Error", "First load the LEBL structure.")
        return
    if not flights:
        messagebox.showerror("Error", "No flights loaded.")
        return

    import datetime
    now = datetime.datetime.now()
    current_minutes = now.hour * 60 + now.minute

    # Reset all gates
    for terminal in bcn_airport.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupied = False
                gate.aircraft_id = None

    assigned_count = 0
    for flight in flights:
        # Necessitem hora d'arribada vàlida
        if flight.time is None:
            continue
        try:
            h, m = flight.time.split(':')
            arr_minutes = int(h) * 60 + int(m)
        except:
            continue

        # L'avió ja ha aterrat (arr_minutes <= ara)
        if arr_minutes > current_minutes:
            continue

        # Comprovem si ja ha sortit (si tenim departure_time)
        if flight.departure_time is not None:
            try:
                hd, md = flight.departure_time.split(':')
                dep_minutes = int(hd) * 60 + int(md)
                if dep_minutes <= current_minutes:
                    continue  # Ja ha sortit, no ocupa porta
            except:
                pass

        # L'avió és a terra: ha arribat i (o no té sortida, o encara no ha sortit)
        origin_ap = FindAirport(all_airports, flight.origin)
        is_schengen = origin_ap.Schengen if origin_ap else False
        if AssignGate(bcn_airport, flight, is_schengen) == 0:
            assigned_count += 1

    # Comptem portes
    total_gates = 0
    free_gates = 0
    for terminal in bcn_airport.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                total_gates += 1
                if not gate.occupied:
                    free_gates += 1

    messagebox.showinfo("Assignment",
                        f"Active flights at {now.strftime('%H:%M')}: {assigned_count}\n"
                        f"Occupied gates: {total_gates - free_gates}\n"
                        f"Free gates: {free_gates}\n"
                        f"Total gates: {total_gates}")

def show_occupancy_ui():
    if not bcn_airport:
        return

    # Let's create a new window to show the status
    top = tk.Toplevel(root)
    top.title("Door Status - LEBL")
    txt = scrolledtext.ScrolledText(top, width=60, height=20)
    txt.pack()

    occupancy = GateOccupancy(bcn_airport)
    txt.insert(tk.END, f"{'DOOR':<15} | {'STATE':<10} | {'AIRCRAFT':<10}\n")
    txt.insert(tk.END, "-" * 40 + "\n")

    for entry in occupancy:
        gate = entry["gate_name"]
        status = entry["status"]
        ac_id = entry["aircraft_id"]
        line = f"{gate:<15} | {status:<10} | {str(ac_id):<10}\n"
        txt.insert(tk.END, line)

    PlotGateOccupancy(bcn_airport)

# ── Funcions de la interfície per a V4 ──────────────────────────────

def load_departures_ui():
    global flights
    filename = filedialog.askopenfilename(
        title="Select Departures file",
        filetypes=[("Text files", "*.txt")]
    )
    if not filename:
        return

    departures = LoadDepartures(filename)

    # Si no hi ha arrivals carregades, usem només les departures
    if len(flights) == 0:
        flights = departures
        messagebox.showinfo("Success", f"Loaded {len(departures)} departures (no arrivals to merge).")
        return

    merged = MergeMovements(flights, departures)

    # MergeMovements pot retornar ([], -1) si alguna llista és buida
    if isinstance(merged, tuple):
        messagebox.showerror("Error", "Could not merge: check that arrivals are loaded first.")
        return

    flights = merged
    messagebox.showinfo("Success", f"Merged successfully. Total movements: {len(flights)}")


def assign_gates_by_hour_ui():
    """
    Simula l'estat de l'aeroport a una hora concreta del dia
    i mostra el gràfic visual de portes (PlotGateOccupancy).
    Això és la funcionalitat extra de V4 que demana el projecte.
    """
    if not bcn_airport:
        messagebox.showerror("Error", "First load the LEBL structure.")
        return
    if not flights:
        messagebox.showerror("Error", "No flights loaded.")
        return

    top = tk.Toplevel(root)
    top.title("Show gate occupancy at hour")
    tk.Label(top, text="Enter hour (0-23):").pack(pady=5)
    entry_hour = tk.Entry(top, width=10)
    entry_hour.pack(pady=5)
    tk.Label(top, text="(Simulates the full day up to this hour)",
             font=("Arial", 8), fg="gray").pack()

    def do_assign():
        try:
            hour_input = int(entry_hour.get().strip())
            if hour_input < 0 or hour_input > 23:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid hour between 0 and 23.")
            return

        # Reset totes les portes
        for terminal in bcn_airport.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    gate.occupied = False
                    gate.aircraft_id = None

        # Assignem avions nocturns primer
        night = NightAircraft(flights)
        if isinstance(night, list) and len(night) > 0:
            AssignNightGates(bcn_airport, night)

        assigned_ids = set()
        if isinstance(night, list):
            for a in night:
                assigned_ids.add(a.aircraft_id)

        # Simulem hora per hora des de 0 fins a l'hora demanada
        total_not_assigned = 0
        h = 0
        while h <= hour_input:
            ref_minutes = h * 60

            # Alliberar avions que surten durant aquesta hora
            for flight in flights:
                if flight.departure_time is not None:
                    try:
                        hd, md = flight.departure_time.split(':')
                        dep_minutes = int(hd) * 60 + int(md)
                        if ref_minutes <= dep_minutes < ref_minutes + 60:
                            FreeGate(bcn_airport, flight.aircraft_id)
                            assigned_ids.discard(flight.aircraft_id)
                    except:
                        pass

            # Assignar avions que arriben durant aquesta hora
            for flight in flights:
                if flight.time is not None:
                    try:
                        ha, ma = flight.time.split(':')
                        arr_minutes = int(ha) * 60 + int(ma)
                        if ref_minutes <= arr_minutes < ref_minutes + 60:
                            if flight.aircraft_id not in assigned_ids:
                                origin_ap = FindAirport(all_airports, flight.origin)
                                is_sch = origin_ap.Schengen if origin_ap else False
                                if AssignGate(bcn_airport, flight, is_sch) == -1:
                                    total_not_assigned += 1
                                else:
                                    assigned_ids.add(flight.aircraft_id)
                    except:
                        pass
            h += 1

        # Comptem estat actual
        total_gates = 0
        occupied_gates = 0
        for terminal in bcn_airport.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    total_gates += 1
                    if gate.occupied:
                        occupied_gates += 1

        top.destroy()

        # Mostrem primer un resum en text
        messagebox.showinfo(
            "Gate status",
            f"State at {hour_input:02d}:00\n"
            f"Occupied gates: {occupied_gates}\n"
            f"Free gates: {total_gates - occupied_gates}\n"
            f"Total gates: {total_gates}\n"
            f"Not assigned (full terminal): {total_not_assigned}"
        )

        # I després el gràfic visual de portes ← LA PART EXTRA DE V4
        PlotGateOccupancy(bcn_airport)

    tk.Button(top, text="Show occupancy", command=do_assign).pack(pady=10)


def plot_day_occupancy_ui():
    """Mostra el gràfic d'ocupació de portes durant tot el dia."""
    if not bcn_airport:
        messagebox.showerror("Error", "First load the LEBL structure.")
        return
    if not flights:
        messagebox.showerror("Error", "No flights loaded.")
        return
    PlotDayOccupancy(bcn_airport, flights)

#Main display:
root = tk.Tk()
root.title("Airport Management")
root.geometry("1000x800") #Interface modified to display al options

#Character customization:
tk.Label(root, text=" Airport Management", font=("Arial", 16, "bold")).pack(pady=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)
#Interface will display the following items:
tk.Button(frame_buttons, text="Load airports ✈️", width=20, command=load_airports).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_buttons, text="Save Schengen 🛂 ", width=20, command=save_schengen).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_buttons, text="See comparison graph 📊", width=20, command=show_plot).grid(row=0, column=2, padx=5, pady=5)
tk.Button(frame_buttons, text="View in Google Earth 🌍", width=20, command=show_map).grid(row=0, column=3, padx=5, pady=5)

#Interface customization code:
frame_add = tk.LabelFrame(root, text="Add / Eliminate airports", padx=10, pady=10)
frame_add.pack(pady=10, fill="x", padx=20)

tk.Label(frame_add, text="ICAO code:").grid(row=0, column=0, sticky="w")
entry_code = tk.Entry(frame_add, width=10)
entry_code.grid(row=0, column=1, padx=5)

#LINES WERE ELIMINATED

tk.Button(frame_add, text="Add", width=10, command=add_airport).grid(row=0, column=2, padx=5)
tk.Button(frame_add, text="Eliminate", width=10, command=remove_airport).grid(row=0, column=3, padx=5)

#Airport list:
tk.Label(root, text="Loaded Airports:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
listbox = tk.Listbox(root, width=100, height=5, font=("Courier", 9)) #Space of loaded airports MAXIMIZED FOR COMFORT
listbox.pack(padx=20, pady=5, fill="both", expand=True)

#We create the version 2 interface, which will be displayed under the old one:

#The new frame:
frame_v2 = tk.LabelFrame(root, text="VERSION 2: ARRIVALS ✈ ️", padx=10, pady=10)
frame_v2.pack(pady=10, fill="x", padx=20)

tk.Button(frame_v2, text="Load Arrivals", width=15, command=load_arrivals_ui).grid(row=0, column=0, padx=5)
tk.Button(frame_v2, text="Plot Hours", width=15, command=lambda: PlotArrivals(flights)).grid(row=0, column=1, padx=5)
tk.Button(frame_v2, text="Plot Airlines", width=15, command=lambda: PlotAirlines(flights)).grid(row=0, column=2, padx=5)
tk.Button(frame_v2, text="Plot Schengen", width=15, command=lambda: PlotFlightsType(flights)).grid(row=0, column=3, padx=5)

tk.Button(frame_v2, text="Save Flights", width=15, command=save_flights_ui).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_v2, text="Map All Flights", width=15, command=lambda: map_flights_ui(False)).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame_v2, text="Map Long Dist", width=15, command=lambda: map_flights_ui(True)).grid(row=1, column=2, padx=5, pady=5)

tk.Button(frame_v2, text="Clear All Arrivals", width=15, command=clear_arrivals,bg='red').grid(row=2, column=0, padx=5, pady=5)
tk.Button(frame_v2, text="Reload Arrivals", width=15, command=reload_arrivals_ui,bg='green').grid(row=2, column=1, padx=5, pady=5)

# We create the version 3 interface, which will be displayed under the old ones:

frame_v3 = tk.LabelFrame(root, text="VERSION 3: GATE MANAGEMENT 🏢", padx=10, pady=10, fg="black")
frame_v3.pack(pady=10, fill="x", padx=20)

tk.Button(frame_v3, text="Data structure LEBL", width=25,
          command=load_lebl_structure).grid(row=0, column=0, padx=5)

tk.Button(frame_v3, text="Assign gates", width=25,
          command=assign_gates_to_flights).grid(row=0, column=1, padx=5)

tk.Button(frame_v3, text="Show gate occupancy", width=25,
          command=show_occupancy_ui).grid(row=0, column=2, padx=5)

frame_v4 = tk.LabelFrame(root, text="VERSION 4: DEPARTURES & DAY PLANNING ✈🌙", padx=10, pady=10)
frame_v4.pack(pady=10, fill="x", padx=20)

tk.Button(frame_v4, text="Load Departures", width=22,
          command=load_departures_ui).grid(row=0, column=0, padx=5)

tk.Button(frame_v4, text="Assign Gates at Hour", width=22,
          command=assign_gates_by_hour_ui).grid(row=0, column=1, padx=5)

tk.Button(frame_v4, text="Plot Day Occupancy", width=22,
          command=plot_day_occupancy_ui).grid(row=0, column=2, padx=5)

tk.Button(frame_v2, text="📊 Day Statistics", width=15,
          command=lambda: DayStatistics(flights)).grid(row=1, column=3, padx=5, pady=5)


# ── RELLOTGE EN TEMPS REAL I PRÒXIMS VOLS (nova funcionalitat)

# Frame del rellotge a la part superior de la interfície
frame_clock = tk.LabelFrame(root, text="🕐 Live Airport Monitor",
                             padx=10, pady=8, fg="darkblue",
                             font=("Arial", 10, "bold"))
frame_clock.pack(pady=5, fill="x", padx=20)

# Rellotge gran
label_clock = tk.Label(frame_clock, text="00:00:00",
                        font=("Courier", 28, "bold"), fg="darkblue")
label_clock.grid(row=0, column=0, rowspan=2, padx=20)

# Separador visual
tk.Label(frame_clock, text="|", font=("Arial", 30), fg="lightgray").grid(
    row=0, column=1, rowspan=2, padx=10)

# Pròxim vol a arribar
tk.Label(frame_clock, text="Next arrival:",
         font=("Arial", 9), fg="gray").grid(row=0, column=2, sticky="w")
label_next_arrival = tk.Label(frame_clock, text="— Load flights —",
                               font=("Arial", 11, "bold"), fg="#27ae60")
label_next_arrival.grid(row=1, column=2, sticky="w")

# Separador
tk.Label(frame_clock, text="|", font=("Arial", 30), fg="lightgray").grid(
    row=0, column=3, rowspan=2, padx=10)

# Pròxima sortida
tk.Label(frame_clock, text="Next departure:",
         font=("Arial", 9), fg="gray").grid(row=0, column=4, sticky="w")
label_next_departure = tk.Label(frame_clock, text="— Load flights —",
                                 font=("Arial", 11, "bold"), fg="#e74c3c")
label_next_departure.grid(row=1, column=4, sticky="w")

# Separador
tk.Label(frame_clock, text="|", font=("Arial", 30), fg="lightgray").grid(
    row=0, column=5, rowspan=2, padx=10)

# Vols actius ara
tk.Label(frame_clock, text="Active flights now:",
         font=("Arial", 9), fg="gray").grid(row=0, column=6, sticky="w")
label_active = tk.Label(frame_clock, text="—",
                         font=("Arial", 11, "bold"), fg="#2980b9")
label_active.grid(row=1, column=6, sticky="w")


def update_clock():
    """
    S'executa cada segon. Actualitza el rellotge i els pròxims vols.
    """
    import datetime
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_minutes = now.hour * 60 + now.minute

    # Actualitzem el rellotge
    label_clock.config(text=current_time)

    if flights:
        # ── Pròxima arribada (la més propera que encara no ha aterrat) ──
        next_arr = None
        next_arr_minutes = 99999
        i = 0
        while i < len(flights):
            f = flights[i]
            if f.time is not None:
                try:
                    h, m = f.time.split(':')
                    arr_min = int(h) * 60 + int(m)
                    # Vols que arriben en els propers 60 minuts
                    if current_minutes <= arr_min <= current_minutes + 60:
                        if arr_min < next_arr_minutes:
                            next_arr_minutes = arr_min
                            next_arr = f
                except:
                    pass
            i += 1

        if next_arr:
            label_next_arrival.config(
                text=f"{next_arr.time}  {next_arr.aircraft_id} ({next_arr.airline})  ← {next_arr.origin}",
                fg="#27ae60"
            )
        else:
            label_next_arrival.config(text="No arrivals in next 60 min", fg="gray")

        # ── Pròxima sortida ──
        next_dep = None
        next_dep_minutes = 99999
        i = 0
        while i < len(flights):
            f = flights[i]
            if f.departure_time is not None:
                try:
                    h, m = f.departure_time.split(':')
                    dep_min = int(h) * 60 + int(m)
                    if current_minutes <= dep_min <= current_minutes + 60:
                        if dep_min < next_dep_minutes:
                            next_dep_minutes = dep_min
                            next_dep = f
                except:
                    pass
            i += 1

        if next_dep:
            dest = next_dep.destination if next_dep.destination else "?"
            label_next_departure.config(
                text=f"{next_dep.departure_time}  {next_dep.aircraft_id} ({next_dep.airline})  → {dest}",
                fg="#e74c3c"
            )
        else:
            label_next_departure.config(text="No departures in next 60 min", fg="gray")

        # ── Vols actius ara (han arribat i no han sortit) ──
        active = 0
        i = 0
        while i < len(flights):
            f = flights[i]
            if f.time is not None:
                try:
                    h, m = f.time.split(':')
                    arr_min = int(h) * 60 + int(m)
                    if arr_min <= current_minutes:
                        # Comprovem si ja ha sortit
                        already_departed = False
                        if f.departure_time is not None:
                            hd, md = f.departure_time.split(':')
                            dep_min = int(hd) * 60 + int(md)
                            if dep_min <= current_minutes:
                                already_departed = True
                        if not already_departed:
                            active += 1
                except:
                    pass
            i += 1

        label_active.config(text=f"{active} aircraft on ground")

    # Tornem a cridar cada 1000ms (1 segon)
    root.after(1000, update_clock)


# Iniciem el rellotge
update_clock()
root.mainloop()
