import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from airport import *

# Variable global para la lista de aeropuertos
airports = []

# ── FUNCIONES DE LA INTERFAZ ──────────────────────────────────────

def load_airports():
    global airports
    filename = filedialog.askopenfilename(
        title="Selecciona archivo de aeropuertos",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        airports = LoadAirports(filename)
        for ap in airports:
            SetSchengen(ap)
        update_listbox()
        messagebox.showinfo("Éxito", f"Se han cargado {len(airports)} aeropuertos.")

def add_airport():
    code = entry_code.get().strip().upper()
    try:
        lat = float(entry_lat.get().strip())
        lon = float(entry_lon.get().strip())
    except ValueError:
        messagebox.showerror("Error", "Latitud y longitud deben ser números.")
        return
    if not code:
        messagebox.showerror("Error", "Introduce un código ICAO.")
        return

    new_ap = airport(code, lat, lon)
    SetSchengen(new_ap)
    AddAirport(airports, new_ap)
    update_listbox()
    entry_code.delete(0, tk.END)
    entry_lat.delete(0, tk.END)
    entry_lon.delete(0, tk.END)

def remove_airport():
    code = entry_code.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Introduce el código ICAO a eliminar.")
        return
    result = RemoveAirport(airports, code)
    if result == -1:
        messagebox.showerror("Error", f"El aeropuerto {code} no existe.")
    else:
        messagebox.showinfo("Éxito", f"Aeropuerto {code} eliminado.")
        update_listbox()
    entry_code.delete(0, tk.END)

def save_schengen():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados.")
        return
    filename = filedialog.asksaveasfilename(
        title="Guardar aeropuertos Schengen",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        result = SaveSchengenAirports(airports, filename)
        if result == -1:
            messagebox.showerror("Error", "No hay aeropuertos Schengen para guardar.")
        else:
            messagebox.showinfo("Éxito", "Aeropuertos Schengen guardados correctamente.")

def show_plot():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados.")
        return
    PlotAirports(airports)

def show_map():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados.")
        return
    MapAirports(airports)
    messagebox.showinfo("KML generado", "Archivo airports.kml generado.\nÁbrelo con Google Earth.")

def update_listbox():
    listbox.delete(0, tk.END)
    for ap in airports:
        schengen_str = "✔ Schengen" if ap.Schengen else "✘ No Schengen"
        listbox.insert(tk.END, f"{ap.code} | Lat: {ap.latitude:.4f} | Lon: {ap.longitude:.4f} | {schengen_str}")

# ── VENTANA PRINCIPAL ─────────────────────────────────────────────

root = tk.Tk()
root.title("Airport Management")
root.geometry("750x600")

# Título
tk.Label(root, text="✈ Airport Management", font=("Arial", 16, "bold")).pack(pady=10)

# Frame de botones principales
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="Cargar aeropuertos", width=20, command=load_airports).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_buttons, text="Guardar Schengen", width=20, command=save_schengen).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_buttons, text="Ver gráfico", width=20, command=show_plot).grid(row=0, column=2, padx=5, pady=5)
tk.Button(frame_buttons, text="Ver en Google Earth", width=20, command=show_map).grid(row=0, column=3, padx=5, pady=5)

# Frame para añadir/eliminar aeropuertos
frame_add = tk.LabelFrame(root, text="Añadir / Eliminar aeropuerto", padx=10, pady=10)
frame_add.pack(pady=10, fill="x", padx=20)

tk.Label(frame_add, text="Código ICAO:").grid(row=0, column=0, sticky="w")
entry_code = tk.Entry(frame_add, width=10)
entry_code.grid(row=0, column=1, padx=5)

tk.Label(frame_add, text="Latitud:").grid(row=0, column=2, sticky="w")
entry_lat = tk.Entry(frame_add, width=10)
entry_lat.grid(row=0, column=3, padx=5)

tk.Label(frame_add, text="Longitud:").grid(row=0, column=4, sticky="w")
entry_lon = tk.Entry(frame_add, width=10)
entry_lon.grid(row=0, column=5, padx=5)

tk.Button(frame_add, text="Añadir", width=10, command=add_airport).grid(row=0, column=6, padx=5)
tk.Button(frame_add, text="Eliminar", width=10, command=remove_airport).grid(row=0, column=7, padx=5)

# Lista de aeropuertos
tk.Label(root, text="Lista de aeropuertos:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
listbox = tk.Listbox(root, width=100, height=20, font=("Courier", 9))
listbox.pack(padx=20, pady=5, fill="both", expand=True)

root.mainloop()


