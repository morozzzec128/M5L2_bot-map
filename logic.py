import sqlite3
import os
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__ (self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
        fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_global()
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lon = coordinates
                ax.plot(lon, lat, marker='o', color='red', markersize=5, transform=ccrs.PlateCarree())
                ax.text(lon + 1, lat, city, fontsize=9, transform=ccrs.PlateCarree())
        
        plt.savefig(path, dpi=300)
        plt.close()

    def draw_distance(self, city1, city2):
        pass

    def get_city_map(self, city_name):
        coordinates = self.get_coordinates(city_name)
        if not coordinates:
            return None  # Город не найден
    

        
        lat, lon = coordinates
        path = f"maps/{city_name}.png"
        os.makedirs("maps", exist_ok=True)  # Создаем папку, если ее нет

        fig, ax = plt.subplots(figsize=(8, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([lon - 5, lon + 5, lat - 5, lat + 5])  # Задаем область вокруг города

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.COASTLINE)

        ax.plot(lon, lat, marker='o', color='red', markersize=6, transform=ccrs.PlateCarree())
        ax.text(lon + 0.5, lat, city_name, fontsize=12, transform=ccrs.PlateCarree())

        plt.savefig(path, dpi=300)
        plt.close()

        return path
    
    def get_multiple_cities_map(self, cities):
        """Создает карту с отмеченными городами."""
        if not cities:
            return None

        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={"projection": ccrs.PlateCarree()})
        ax.stock_img()

        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lon = coords
                ax.plot(lon, lat, marker='o', markersize=5, color='red', transform=ccrs.PlateCarree())
                ax.text(lon, lat, city, transform=ccrs.PlateCarree(), fontsize=8, color='black')

        image_path = "multiple_cities_map.png"
        plt.savefig(image_path, bbox_inches='tight')
        plt.close()
        return image_path


m = DB_Map(DATABASE)
m.create_user_table()