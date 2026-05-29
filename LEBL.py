import os
from airport import LoadAirports, FindAirport
from aircraft import NightAircraft
all_airports_cache = LoadAirports("Airports.txt")

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

    if end_gate <= init_gate:
        return -1

    # 2. Drop previous list of gates
    area.gates = []

    gate_num = init_gate
    while gate_num <= end_gate:
        gate_name = f"{prefix}{gate_num}"
        # We create the object Gate i we added to the area
        new_gate = Gate(gate_name)
        area.gates.append(new_gate)
        gate_num += 1

    return 0

def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"

    #We check if the file exists
    if not os.path.exists(filename):
        return -1 #File doesn't exist

    #If the file exists...
    terminal.airlines = []

    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line:
                parts = line.split()
                icao_code = parts[-1] #The ICAO code is the las element of the line
                terminal.airlines.append(icao_code)
            i += 1
        return 0

    except Exception:
        return -1

def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        return None
    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        header = lines[0].split()
        icao_code = header[0]
        num_terminals = int(header[1])

        airport = BarcelonaAP(icao_code)

        current_line = 1
        t_count = 0

        while t_count < num_terminals:
            t_data = lines[current_line].split()
            t_name = t_data[1]
            num_areas = int(t_data[2])

            terminal_obj = Terminal(t_name)

            LoadAirlines(terminal_obj, t_name)

            current_line += 1
            a_count = 0

            while a_count < num_areas:
                a_data = lines[current_line].split()
                area_name = a_data[1]
                area_type = a_data[2]
                init_g = int(a_data[4])
                end_g = int(a_data[6])

                area_obj = BoardingArea(area_name, area_type)

                gate_prefix = f"{t_name}{area_name}G"
                SetGates(area_obj, init_g, end_g, gate_prefix)

                terminal_obj.boarding_areas.append(area_obj)

                current_line += 1
                a_count += 1

            airport.terminals.append(terminal_obj)
            t_count += 1

        return airport

    except Exception:
        return None
def GateOccupancy(bcn):
    result = []

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            g = 0
            while g < len(area.gates):
                gate = area.gates[g]
                result.append({
                    "gate_name": gate.name,
                    "status": "occupied" if gate.occupied else "free",
                    "aircraft_id": gate.aircraft_id
                })
                g += 1
            a += 1
        t += 1

    return result

def IsAirlineInTerminal(terminal,name):
    if name == '':
        return False
    if len (terminal.airlines) ==0: #Empty list
        return False
    i=0
    while i< len(terminal.airlines):
        if terminal.airlines[i]==name:
            return True
        i+=1
    return False

def SearchTerminal(bcn,name):
    i=0
    while i<len(bcn.terminals):
        if IsAirlineInTerminal(bcn.terminals[i],name):
            return bcn.terminals[i].name
        i+=1
    return ''


def AssignGate(bcn, aircraft, is_schengen):
    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        # Millora: si no trobem l'airline, intentem cada terminal
        # en lloc d'anar sempre a T1
        a = 0
        while a < len(bcn.terminals):
            terminal = bcn.terminals[a]
            g_idx = 0
            while g_idx < len(terminal.boarding_areas):
                area = terminal.boarding_areas[g_idx]
                g = 0
                while g < len(area.gates):
                    if not area.gates[g].occupied:
                        area.gates[g].occupied = True
                        area.gates[g].aircraft_id = aircraft.aircraft_id
                        return 0
                    g += 1
                g_idx += 1
            a += 1
        return -1  # Cap porta lliure en cap terminal

    # Cas normal: airline trobada, busquem al seu terminal
    terminal = None
    i = 0
    while i < len(bcn.terminals):
        if bcn.terminals[i].name == terminal_name:
            terminal = bcn.terminals[i]
        i += 1

    if terminal is None:
        return -1

    # Primer intentem trobar porta del tipus correcte (Schengen/no-Schengen)
    a = 0
    while a < len(terminal.boarding_areas):
        area = terminal.boarding_areas[a]
        if area.type.lower() == "schengen" and is_schengen:
            g = 0
            while g < len(area.gates):
                if not area.gates[g].occupied:
                    area.gates[g].occupied = True
                    area.gates[g].aircraft_id = aircraft.aircraft_id
                    return 0
                g += 1
        elif area.type.lower() != "schengen" and not is_schengen:
            g = 0
            while g < len(area.gates):
                if not area.gates[g].occupied:
                    area.gates[g].occupied = True
                    area.gates[g].aircraft_id = aircraft.aircraft_id
                    return 0
                g += 1
        a += 1

    # Fallback: qualsevol porta lliure al terminal correcte
    a = 0
    while a < len(terminal.boarding_areas):
        g = 0
        while g < len(terminal.boarding_areas[a].gates):
            if not terminal.boarding_areas[a].gates[g].occupied:
                terminal.boarding_areas[a].gates[g].occupied = True
                terminal.boarding_areas[a].gates[g].aircraft_id = aircraft.aircraft_id
                return 0
            g += 1
        a += 1
    return -1

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def PlotGateOccupancy(bcn):
    if not bcn:
        return

    num_terminals = len(bcn.terminals)
    fig, axes = plt.subplots(1, num_terminals, figsize=(8 * num_terminals, 12))

    if num_terminals == 1:
        axes = [axes]

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        ax = axes[t]
        ax.set_title(terminal.name, fontsize=13, fontweight='bold', pad=15)
        ax.axis('off')

        num_areas = len(terminal.boarding_areas)

        # Find max gates in any area to set y scale
        max_gates = 1
        a = 0
        while a < len(terminal.boarding_areas):
            if len(terminal.boarding_areas[a].gates) > max_gates:
                max_gates = len(terminal.boarding_areas[a].gates)
            a += 1

        total_height = max_gates * 1.2 + 3
        ax.set_xlim(0, num_areas * 6 + 2)
        ax.set_ylim(0, total_height)

        # Top horizontal terminal bar
        ax.plot([0.5, num_areas * 6 + 1.5], [total_height - 0.5, total_height - 0.5],
                color='steelblue', linewidth=10, solid_capstyle='butt')

        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            x_center = 1 + a * 6 + 2.5

            num_gates = len(area.gates)

            # Vertical spine
            ax.plot([x_center, x_center], [1.2, total_height - 0.5],
                    color='steelblue', linewidth=6, solid_capstyle='butt')

            # Area label at bottom
            ax.text(x_center, 0.4, area.name, ha='center', fontsize=9,
                    fontweight='bold', color='steelblue')

            if num_gates == 0:
                a += 1
                continue

            gate_spacing = (total_height - 2.5) / max_gates

            g = 0
            while g < num_gates:
                gate = area.gates[g]
                y = 1.5 + g * gate_spacing
                color = 'red' if gate.occupied else 'limegreen'

                rect_w = 2.2
                rect_h = min(gate_spacing * 0.55, 0.9)

                if g % 2 == 0:
                    x_rect = x_center - rect_w - 0.3
                    x_connector_end = x_rect + rect_w
                    x_label = x_rect - 0.1
                    ha = 'right'
                else:
                    x_rect = x_center + 0.3
                    x_connector_end = x_rect
                    x_label = x_rect + rect_w + 0.1
                    ha = 'left'

                rect = mpatches.FancyBboxPatch(
                    (x_rect, y - rect_h / 2), rect_w, rect_h,
                    boxstyle="round,pad=0.05",
                    color=color, zorder=3)
                ax.add_patch(rect)

                # Connector line
                ax.plot([x_center, x_connector_end], [y, y],
                        color='steelblue', linewidth=1.5, zorder=2)

                # Label
                font_size = max(4, min(7, gate_spacing * 3))
                if gate.occupied:
                    label = f"{gate.name}\n{gate.aircraft_id}"
                else:
                    label = gate.name
                ax.text(x_label, y, label, ha=ha, va='center',
                        fontsize=font_size, color='black')

                g += 1
            a += 1
        t += 1

    free_patch = mpatches.Patch(color='limegreen', label='Free')
    occupied_patch = mpatches.Patch(color='red', label='Occupied')
    fig.legend(handles=[free_patch, occupied_patch], loc='lower center',
               ncol=2, fontsize=10, bbox_to_anchor=(0.5, 0.01))

    plt.suptitle(f"Gate Occupancy - {bcn.code}", fontsize=15, fontweight='bold')
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    plt.show()


if __name__ == "__main__":
    bcn = LoadAirportStructure("Terminals.txt")
    if bcn:
        print(f"Loaded: {bcn.code}")
        for t in bcn.terminals:
            print(f"  Terminal {t.name}, airlines: {t.airlines[:5]}")
            for a in t.boarding_areas:
                print(f"    Area {a.name} type={a.type} gates={len(a.gates)}")
    else:
        print("ERROR: Could not load Terminals.txt")

def AssignNightGates(bcn, aircrafts):
    if len(aircrafts) == 0:
        return -1

    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        if a.time is None:
            # Busquem el terminal correcte per airline
            # Si no té airline coneguda, AssignGate ja fa el fallback a T1
            # is_schengen=False perquè avions nocturns no tenen origen conegut
            AssignGate(bcn, a, is_schengen=False)
        i += 1
    return 0


def FreeGate(bcn, aircraft_id):
    """
    Allibera la porta assignada a l'aeronau amb l'id rebut.
    Retorna 0 si la troba i allibera, -1 si no la troba.
    """
    if not bcn:
        return -1

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            g = 0
            while g < len(area.gates):
                gate = area.gates[g]
                if gate.occupied and gate.aircraft_id == aircraft_id:
                    gate.occupied = False
                    gate.aircraft_id = None  # Porta lliure
                    return 0
                g += 1
            a += 1
        t += 1
    return -1  # No s'ha trobat cap porta amb aquest avió


def AssignGatesAtTime(bcn, aircrafts, time):
    """
    Actualitza l'estat de bcn per a una hora concreta del dia:
    1. Allibera les portes dels avions que ja han sortit (departure_time <= time)
    2. Assigna portes als avions que aterren durant la franja d'una hora
    Retorna el nombre d'avions que no s'han pogut assignar per manca de portes.
    """
    h_ref, m_ref = time.split(':')
    ref_minutes = int(h_ref) * 60 + int(m_ref)
    end_minutes = ref_minutes + 60  # Finestra d'una hora

    # Pas 1: Alliberar portes dels avions que ja han sortit ABANS d'aquesta hora
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        if a.departure_time is not None:
            h_dep, m_dep = a.departure_time.split(':')
            dep_minutes = int(h_dep) * 60 + int(m_dep)
            if dep_minutes <= ref_minutes:
                FreeGate(bcn, a.aircraft_id)
        i += 1

    # Pas 2: Assignar portes als avions que aterren en aquesta franja horària
    # Primer construïm un conjunt dels ids que JA tenen porta ocupada
    occupied_ids = set()
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if gate.occupied and gate.aircraft_id is not None:
                    occupied_ids.add(gate.aircraft_id)

    not_assigned = 0
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        if a.time is not None:
            h_arr, m_arr = a.time.split(':')
            arr_minutes = int(h_arr) * 60 + int(m_arr)
            # Avió dins la finestra d'una hora i sense porta ja assignada
            if ref_minutes <= arr_minutes < end_minutes:
                if a.aircraft_id not in occupied_ids:  # ← EVITA REASSIGNAR
                    origin_ap = FindAirport(all_airports_cache, a.origin)
                    is_sch = origin_ap.Schengen if origin_ap else False
                    if AssignGate(bcn, a, is_sch) == -1:
                        not_assigned += 1
                    else:
                        occupied_ids.add(a.aircraft_id)  # Marca com assignat
        i += 1

    return not_assigned


def PlotDayOccupancy(bcn, aircrafts):
    """
    Simula tot el dia minut a minut (per hores) i mostra:
    - Portes ocupades per terminal a cada hora
    - Avions no assignats per manca de portes a cada hora
    """
    hours = list(range(24))
    terminal_names = [t.name for t in bcn.terminals]

    occupancy_per_terminal = {}
    for t in bcn.terminals:
        occupancy_per_terminal[t.name] = [0] * 24

    not_assigned_per_hour = [0] * 24

    # Reiniciem totes les portes per simular des del principi del dia
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupied = False
                gate.aircraft_id = None

    # Assignem primer els avions nocturns (sense hora d'arribada, només sortida)
    night = NightAircraft(aircrafts)
    if isinstance(night, list) and len(night) > 0:
        AssignNightGates(bcn, night)

    # Conjunt d'avions ja assignats (per no reassignar)
    assigned_ids = set()
    # Afegim els nocturns com ja assignats
    if isinstance(night, list):
        for a in night:
            assigned_ids.add(a.aircraft_id)

    # Simulem hora per hora de forma acumulativa
    h = 0
    while h < 24:
        ref_minutes = h * 60  # Inici de la franja (ex: hora 10 = 600 minuts)

        # Pas 1: Alliberar portes dels avions que SURTEN en algun moment
        # FINS A la fi d'aquesta hora (és a dir, departure_time < ref_minutes + 60)
        # Però només els que ja havien arribat (tenen time != None o són nocturns)
        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]
            if a.departure_time is not None:
                try:
                    hd, md = a.departure_time.split(':')
                    dep_minutes = int(hd) * 60 + int(md)
                    # L'avió surt durant aquesta hora
                    if ref_minutes <= dep_minutes < ref_minutes + 60:
                        FreeGate(bcn, a.aircraft_id)
                        # Ja no el considerem assignat (pot tornar a arribar)
                        if a.aircraft_id in assigned_ids:
                            assigned_ids.discard(a.aircraft_id)
                except:
                    pass
            i += 1

        # Pas 2: Assignar portes als avions que ARRIBEN durant aquesta hora
        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]
            if a.time is not None:
                try:
                    ha, ma = a.time.split(':')
                    arr_minutes = int(ha) * 60 + int(ma)
                    # Arriba durant aquesta hora i no té porta ja
                    if ref_minutes <= arr_minutes < ref_minutes + 60:
                        if a.aircraft_id not in assigned_ids:
                            origin_ap = FindAirport(all_airports_cache, a.origin)
                            is_sch = origin_ap.Schengen if origin_ap else False
                            if AssignGate(bcn, a, is_sch) == -1:
                                not_assigned_per_hour[h] += 1  # No hi havia porta
                            else:
                                assigned_ids.add(a.aircraft_id)
                except:
                    pass
            i += 1

        # Pas 3: Comptem portes ocupades per terminal AL FINAL d'aquesta hora
        for terminal in bcn.terminals:
            count = 0
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if gate.occupied:
                        count += 1
            occupancy_per_terminal[terminal.name][h] = count

        h += 1

    # ── Dibuixem els gràfics ──────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    # Gràfic 1: Ocupació per terminal (una línia per terminal)
    for t_name in terminal_names:
        ax1.plot(hours, occupancy_per_terminal[t_name], marker='o', label=t_name)
    ax1.set_title("Gate occupancy per terminal throughout the day")
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Occupied gates")
    ax1.set_xticks(hours)
    ax1.legend()
    ax1.grid(True)

    # Gràfic 2: Avions no assignats per hora (valors enters)
    ax2.bar(hours, not_assigned_per_hour, color='red', alpha=0.7)
    ax2.set_title("Aircraft not assigned per hour (no free gates)")
    ax2.set_xlabel("Hour")
    ax2.set_ylabel("Aircraft not assigned")
    ax2.set_xticks(hours)
    ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax2.set_ylim(bottom=0)  # ← Evita valors negatius a l'eix Y
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    bcn = LoadAirportStructure("Terminals.txt")
    if bcn:
        print(f"Loaded: {bcn.code}")
        for t in bcn.terminals:
            print(f"  Terminal {t.name}, airlines: {t.airlines[:5]}")
            for a in t.boarding_areas:
                print(f"    Area {a.name} type={a.type} gates={len(a.gates)}")

        # Test FreeGate
        result = FreeGate(bcn, "XXXX")
        print(f"FreeGate inexistent: {result}")  # Ha de ser -1

        # Test AssignNightGates amb llista buida
        result = AssignNightGates(bcn, [])
        print(f"AssignNightGates buit: {result}")  # Ha de ser -1

    else:
        print("ERROR: Could not load Terminals.txt")