from tkinter import *
import tkintermapview
import requests
from bs4 import BeautifulSoup

root = Tk()
root.title('System mapowy — Stacje, Pracownicy, Klienci')
root.geometry('1200x800')

# -------------------------------
# Mapa
# -------------------------------
map_widget = tkintermapview.TkinterMapView(root, width=1150, height=400)
map_widget.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
map_widget.set_position(52.23, 21.00)
map_widget.set_zoom(6)

# -------------------------------
# Klasa i dane
# -------------------------------
class MapEntity:
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=self.name)

    def get_coordinates(self):
        url = f'https://pl.wikipedia.org/wiki/{self.location}'
        r = requests.get(url).text
        html = BeautifulSoup(r, 'html.parser')
        lat = float(html.select('.latitude')[1].text.replace(',', '.'))
        lon = float(html.select('.longitude')[1].text.replace(',', '.'))
        return [lat, lon]

stations, employees, clients = [], [], []

# -------------------------------
# Funkcje
# -------------------------------
def add_entity(list_, entry_name, location_input, show_fn, is_entry=True):
    name = entry_name.get().strip()
    location = location_input.get().strip() if is_entry else get_location_from_station_name(location_input.get())
    if not name or not location:
        return
    list_.append(MapEntity(name, location))
    entry_name.delete(0, END)
    location_input.set('') if not is_entry else location_input.delete(0, END)
    show_fn()

def get_location_from_station_name(station_name):
    station = next((s for s in stations if s.name == station_name), None)
    return station.location if station else ''

def remove_entity(list_, listbox, show_fn):
    i = listbox.index(ACTIVE)
    list_[i].marker.delete()
    list_.pop(i)
    show_fn()

def edit_entity(list_, listbox, entry_name, location_input, button_edit, show_fn, is_entry=True):
    i = listbox.index(ACTIVE)
    entry_name.delete(0, END)
    entry_name.insert(0, list_[i].name)
    value = list_[i].location if is_entry else list_[i].name
    location_input.set(value) if not is_entry else location_input.insert(0, value)
    button_edit.config(text="Zapisz", command=lambda: update_entity(list_, i, entry_name, location_input, button_edit, show_fn, is_entry))

def update_entity(list_, i, entry_name, location_input, button_edit, show_fn, is_entry=True):
    list_[i].marker.delete()
    name = entry_name.get().strip()
    location = location_input.get().strip() if is_entry else get_location_from_station_name(location_input.get())
    if not name or not location:
        return
    list_[i].name = name
    list_[i].location = location
    list_[i].coordinates = list_[i].get_coordinates()
    list_[i].marker = map_widget.set_marker(*list_[i].coordinates, text=list_[i].name)
    entry_name.delete(0, END)
    location_input.set('') if not is_entry else location_input.delete(0, END)
    button_edit.config(text="Dodaj", command=lambda: add_entity(list_, entry_name, location_input, show_fn, is_entry))
    show_fn()

def show_entities(list_, listbox):
    listbox.delete(0, END)
    for idx, ent in enumerate(list_):
        listbox.insert(idx, f"{idx + 1}. {ent.name} — {ent.location}")

# -------------------------------
# GUI sekcja
# -------------------------------
def create_section(parent, title, list_, col, is_station=False):
    Label(parent, text=title, font=("Arial", 12, "bold")).grid(row=0, column=col, columnspan=2, pady=(5, 0))

    listbox = Listbox(parent, width=35, height=8)
    listbox.grid(row=1, column=col, columnspan=2, padx=10)

    Label(parent, text="Nazwa:").grid(row=2, column=col, sticky=E)
    e_name = Entry(parent, width=20); e_name.grid(row=2, column=col+1, sticky=W, pady=2)

    if is_station:
        Label(parent, text="Lokalizacja:").grid(row=3, column=col, sticky=E)
        e_loc = Entry(parent, width=20); e_loc.grid(row=3, column=col+1, sticky=W, pady=2)
    else:
        Label(parent, text="Stacja:").grid(row=3, column=col, sticky=E)
        var_loc = StringVar()
        e_loc = var_loc
        dropdown = OptionMenu(parent, var_loc, '')
        dropdown.config(width=18)
        dropdown.grid(row=3, column=col+1, sticky=W, pady=2)

        def update_dropdown():
            dropdown['menu'].delete(0, 'end')
            for s in stations:
                dropdown['menu'].add_command(label=s.name, command=lambda value=s.name: var_loc.set(value))
        update_dropdown_funcs.append(update_dropdown)

    def refresh_add():
        add_entity(list_, e_name, e_loc, lambda: show_entities(list_, listbox), is_station)
        for f in update_dropdown_funcs:
            f()

    btn_add = Button(parent, text="Dodaj", width=12, command=refresh_add)
    btn_add.grid(row=4, column=col, pady=2)

    btn_edit = Button(parent, text="Edytuj", width=12,
                      command=lambda: edit_entity(list_, listbox, e_name, e_loc, btn_add,
                                                  lambda: show_entities(list_, listbox), is_station))
    btn_edit.grid(row=4, column=col+1, pady=2)

    btn_del = Button(parent, text="Usuń", width=26,
                     command=lambda: remove_entity(list_, listbox, lambda: show_entities(list_, listbox)))
    btn_del.grid(row=5, column=col, columnspan=2, pady=2)

    return listbox

# -------------------------------
# Ramki i kolejność sekcji
# -------------------------------
frame_top = Frame(root)
frame_top.grid(row=1, column=0, columnspan=3, pady=10)

update_dropdown_funcs = []

lb_st = create_section(frame_top, "Stacje", stations, 0, is_station=True)
lb_emp = create_section(frame_top, "Pracownicy", employees, 2)
lb_cl = create_section(frame_top, "Klienci", clients, 4)

# -------------------------------
# Panel z filtrowaniem mapy
# -------------------------------
frame_controls = Frame(root)
frame_controls.grid(row=1, column=3, padx=10, sticky=N)

Label(frame_controls, text="Widok mapy:", font=("Arial", 12, "bold")).pack(pady=(0, 10))

def show_only(list_):
    map_widget.delete_all_marker()
    for ent in list_:
        ent.marker = map_widget.set_marker(ent.coordinates[0], ent.coordinates[1], text=ent.name)

Button(frame_controls, text="Pokaż stacje", width=18, command=lambda: show_only(stations)).pack(pady=5)
Button(frame_controls, text="Pokaż pracowników", width=18, command=lambda: show_only(employees)).pack(pady=5)
Button(frame_controls, text="Pokaż klientów", width=18, command=lambda: show_only(clients)).pack(pady=5)

def show_employees_selected_station():
    sel = lb_st.curselection()
    if not sel:
        return
    target_loc = stations[sel[0]].location
    map_widget.delete_all_marker()
    for ent in (e for e in employees if e.location == target_loc):
        ent.marker = map_widget.set_marker(ent.coordinates[0], ent.coordinates[1], text=ent.name)

def show_clients_selected_station():
    sel = lb_st.curselection()
    if not sel:
        return
    target_loc = stations[sel[0]].location
    map_widget.delete_all_marker()
    for ent in (c for c in clients if c.location == target_loc):
        ent.marker = map_widget.set_marker(ent.coordinates[0], ent.coordinates[1], text=ent.name)

Button(frame_controls, text="Pracownicy stacji",  width=18, command=show_employees_selected_station).pack(pady=5)
Button(frame_controls, text="Klienci stacji",     width=18, command=show_clients_selected_station).pack(pady=5)

root.mainloop()
