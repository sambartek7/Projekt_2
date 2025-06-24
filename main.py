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

root.mainloop()