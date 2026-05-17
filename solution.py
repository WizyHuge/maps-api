import sys
import math
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt

map_key = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
geocoder_key = "8013b162-6b42-4997-9691-77b7074026e0"
search_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

MAP_WIDTH = 600
MAP_HEIGHT = 450


class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lon = 37.6176
        self.lat = 55.7558
        self.z = 10
        self.theme = "light"
        self.pt = ""
        self.toponym_data = None
        self.full_address = ""
        self.postal_code = ""
        self.setGeometry(100, 100, 600, 500)
        self.setWindowTitle("Карта")
        self.label = QLabel(self)
        self.label.move(0, 0)
        self.label.resize(MAP_WIDTH, MAP_HEIGHT)
        self.btn_theme = QPushButton("Тёмная тема", self)
        self.btn_theme.move(10, 455)
        self.btn_theme.resize(120, 25)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.search_input = QLineEdit(self)
        self.search_input.move(140, 455)
        self.search_input.resize(340, 25)
        self.search_input.returnPressed.connect(self.search)
        self.btn_search = QPushButton("Искать", self)
        self.btn_search.move(490, 455)
        self.btn_search.resize(100, 25)
        self.btn_search.clicked.connect(self.search)
        self.btn_reset = QPushButton("Сброс", self)
        self.btn_reset.move(490, 420)
        self.btn_reset.resize(100, 25)
        self.btn_reset.clicked.connect(self.reset_search)
        self.address_label = QLabel(self)
        self.address_label.move(10, 420)
        self.address_label.resize(470, 25)
        self.cb_postcode = QCheckBox("Почтовый индекс", self)
        self.cb_postcode.move(10, 475)
        self.cb_postcode.stateChanged.connect(self.update_address)
        self.load_map()

    def load_map(self):
        params = {
            "ll": f"{self.lon},{self.lat}",
            "z": self.z,
            "theme": self.theme,
            "apikey": map_key
        }
        if self.pt:
            params["pt"] = self.pt
        resp = requests.get("https://static-maps.yandex.ru/v1", params=params)
        with open("map.png", "wb") as f:
            f.write(resp.content)
        self.label.setPixmap(QPixmap("map.png"))

    def update_address(self):
        if not self.full_address:
            self.address_label.clear()
            return
        if self.cb_postcode.isChecked() and self.postal_code:
            self.address_label.setText(f"{self.full_address}, {self.postal_code}")
        else:
            self.address_label.setText(self.full_address)

    def reset_search(self):
        self.pt = ""
        self.toponym_data = None
        self.full_address = ""
        self.postal_code = ""
        self.search_input.clear()
        self.address_label.clear()
        self.load_map()

    def search(self):
        text = self.search_input.text().strip()
        if not text:
            return
        resp = requests.get("http://geocode-maps.yandex.ru/1.x/", params={
            "apikey": geocoder_key,
            "geocode": text,
            "format": "json"
        })
        members = resp.json()["response"]["GeoObjectCollection"]["featureMember"]
        if not members:
            return
        toponym = members[0]["GeoObject"]
        self.lon, self.lat = toponym["Point"]["pos"].split(" ")
        self.lon = float(self.lon)
        self.lat = float(self.lat)
        self.pt = f"{self.lon},{self.lat},pm2rdm"
        self.toponym_data = toponym
        meta = toponym["metaDataProperty"]["GeocoderMetaData"]
        self.full_address = meta["text"]
        self.postal_code = meta.get("Address", {}).get("postal_code", "")
        self.update_address()
        self.load_map()

    def search_by_coords(self, lon, lat):
        resp = requests.get("http://geocode-maps.yandex.ru/1.x/", params={
            "apikey": geocoder_key,
            "geocode": f"{lon},{lat}",
            "format": "json"
        })
        members = resp.json()["response"]["GeoObjectCollection"]["featureMember"]
        if not members:
            return
        toponym = members[0]["GeoObject"]
        obj_lon, obj_lat = toponym["Point"]["pos"].split(" ")
        self.pt = f"{float(obj_lon)},{float(obj_lat)},pm2rdm"
        self.toponym_data = toponym
        meta = toponym["metaDataProperty"]["GeocoderMetaData"]
        self.full_address = meta["text"]
        self.postal_code = meta.get("Address", {}).get("postal_code", "")
        self.update_address()
        self.load_map()

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
            self.btn_theme.setText("Светлая тема")
        else:
            self.theme = "light"
            self.btn_theme.setText("Тёмная тема")
        self.load_map()

    def move_step(self):
        return 360 / (2 ** self.z)

    def keyPressEvent(self, event):
        step = self.move_step()
        if event.key() == Qt.Key.Key_PageUp:
            if self.z < 17:
                self.z += 1
                self.load_map()
        elif event.key() == Qt.Key.Key_PageDown:
            if self.z > 1:
                self.z -= 1
                self.load_map()
        elif event.key() == Qt.Key.Key_Up:
            self.lat = min(85, self.lat + step)
            self.load_map()
        elif event.key() == Qt.Key.Key_Down:
            self.lat = max(-85, self.lat - step)
            self.load_map()
        elif event.key() == Qt.Key.Key_Left:
            self.lon = max(-180, self.lon - step)
            self.load_map()
        elif event.key() == Qt.Key.Key_Right:
            self.lon = min(180, self.lon + step)
            self.load_map()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            y = event.position().y()
            if 0 <= x <= MAP_WIDTH and 0 <= y <= MAP_HEIGHT:
                lon_span = 360 / (2 ** self.z)
                lat_span = 180 / (2 ** self.z)
                lon = self.lon + (x - MAP_WIDTH / 2) * lon_span / 256
                lat = self.lat - (y - MAP_HEIGHT / 2) * lat_span / 256
                self.search_by_coords(lon, lat)
        elif event.button() == Qt.MouseButton.RightButton:
            x = event.position().x()
            y = event.position().y()
            if 0 <= x <= MAP_WIDTH and 0 <= y <= MAP_HEIGHT:
                lon_span = 360 / (2 ** self.z)
                lat_span = 180 / (2 ** self.z)
                lon = self.lon + (x - MAP_WIDTH / 2) * lon_span / 256
                lat = self.lat - (y - MAP_HEIGHT / 2) * lat_span / 256
                self.search_org(lon, lat)

    def search_org(self, lon, lat):
        resp = requests.get("http://geocode-maps.yandex.ru/1.x/", params={
            "apikey": geocoder_key,
            "geocode": f"{lon},{lat}",
            "format": "json"
        })
        members = resp.json()["response"]["GeoObjectCollection"]["featureMember"]
        if not members:
            return
        geo = members[0]["GeoObject"]
        org_lon, org_lat = map(float, geo["Point"]["pos"].split())
        dx = (lon - org_lon) * 111320 * math.cos(math.radians(lat))
        dy = (lat - org_lat) * 110540
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 50:
            return
        self.pt = f"{org_lon},{org_lat},pm2blm"
        meta = geo["metaDataProperty"]["GeocoderMetaData"]
        self.full_address = meta["text"]
        self.postal_code = meta.get("Address", {}).get("postal_code", "")
        self.toponym_data = None
        self.update_address()
        self.load_map()


app = QApplication(sys.argv)
w = MapWidget()
w.show()
sys.exit(app.exec())
