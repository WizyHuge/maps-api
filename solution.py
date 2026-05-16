import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt

map_key = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"


class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lon = 37.6176
        self.lat = 55.7558
        self.z = 10
        self.setGeometry(100, 100, 600, 450)
        self.setWindowTitle("Карта")
        self.label = QLabel(self)
        self.label.move(0, 0)
        self.label.resize(600, 450)
        self.load_map()

    def load_map(self):
        resp = requests.get("https://static-maps.yandex.ru/v1", params={
            "ll": f"{self.lon},{self.lat}",
            "z": self.z,
            "apikey": map_key
        })
        with open("map.png", "wb") as f:
            f.write(resp.content)
        self.label.setPixmap(QPixmap("map.png"))

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


app = QApplication(sys.argv)
w = MapWidget()
w.show()
sys.exit(app.exec())
