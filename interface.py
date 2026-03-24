import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from airport import *

# Variable global para la lista de aeropuertos
airports = []

# ── FUNCIONES DE LA INTERFAZ ──────────────────────────────────────

def load_airports():
    global airports
    filename = filedialog.askopenfilename(
        title="Select filed airports",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        airports = LoadAirports(filename)
        for ap in airports:
            SetSchengen(ap)
        update_listbox()
        messagebox.showinfo("Correct", f"You loaded {len(airports)} airports.")

def add_airport():
    code = entry_code.get().strip().upper()
    try:
        lat = float(entry_lat.get().strip())
        lon = float(entry_lon.get().strip())
    except ValueError:
        messagebox.showerror("Error", "Latitude and longitude must be numbers.")
        return
    if not code:
        messagebox.showerror("Error", "Introduce an ICAO code.")
        return

    new_ap = airport(code, latitude, longitude)
    SetSchengen(new_ap)
    AddAirport(airports, new_ap)
    update_listbox()
    entry_code.delete(0, tk.END)
    entry_lat.delete(0, tk.END)
    entry_lon.delete(0, tk.END)

def remove_airport():
    code = entry_code.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Enter the ICAO code of the airport you want to eliminate.")
        return
    result = RemoveAirport(airports, code)
    if result == -1:
        messagebox.showerror("Error", f"The airport {code} isn't registered.")
    else:
        messagebox.showinfo("Success", f"Airport {code} was eliminated.")
        update_listbox()
    entry_code.delete(0, tk.END)

def save_schengen():
    if not airports:
        messagebox.showerror("Error", "No airports were loaded.")
        return
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

def show_plot():
    if not airports:
        messagebox.showerror("Error", "No airports were loaded.")
        return
    PlotAirports(airports)

def show_map():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados.")
        return
    MapAirports(airports)
    messagebox.showinfo("KML created", "File airports.kml was generated.\n Use Google Earth to open it.")

def update_listbox():
    listbox.delete(0, tk.END)
    for ap in airports:
        schengen_str = "✔ Schengen" if ap.Schengen else "✘ Not a Schengen airport"
        listbox.insert(tk.END, f"{ap.code} | Latitude: {ap.latitude:.4f} | Longitude: {ap.longitude:.4f} | {schengen_str}")


root = tk.Tk()
root.title("Airport Management")
root.geometry("750x600")


tk.Label(root, text=" Airport Management", font=("Arial", 16, "bold")).pack(pady=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="Load airports", width=20, command=load_airports).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_buttons, text="Save Schengen", width=20, command=save_schengen).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_buttons, text="See comparison graph", width=20, command=show_plot).grid(row=0, column=2, padx=5, pady=5)
tk.Button(frame_buttons, text="View in Google Earth", width=20, command=show_map).grid(row=0, column=3, padx=5, pady=5)


frame_add = tk.LabelFrame(root, text="Add / Eliminate airports", padx=10, pady=10)
frame_add.pack(pady=10, fill="x", padx=20)

tk.Label(frame_add, text="ICAO code:").grid(row=0, column=0, sticky="w")
entry_code = tk.Entry(frame_add, width=10)
entry_code.grid(row=0, column=1, padx=5)

tk.Label(frame_add, text="Latitude:").grid(row=0, column=2, sticky="w")
entry_lat = tk.Entry(frame_add, width=10)
entry_lat.grid(row=0, column=3, padx=5)

tk.Label(frame_add, text="Longitude:").grid(row=0, column=4, sticky="w")
entry_lon = tk.Entry(frame_add, width=10)
entry_lon.grid(row=0, column=5, padx=5)

tk.Button(frame_add, text="Add", width=10, command=add_airport).grid(row=0, column=6, padx=5)
tk.Button(frame_add, text="Eliminate", width=10, command=remove_airport).grid(row=0, column=7, padx=5)

# Lista de aeropuertos
tk.Label(root, text="Airport list:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
listbox = tk.Listbox(root, width=100, height=20, font=("Courier", 9))
listbox.pack(padx=20, pady=5, fill="both", expand=True)

root.mainloop()


