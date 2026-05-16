import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

map_key = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

lon = "37.6176"
lat = "55.7558"
z = "10"

resp = requests.get("https://static-maps.yandex.ru/v1", params={
    "ll": f"{lon},{lat}",
    "z": z,
    "apikey": map_key
})

with open("map.png", "wb") as f:
    f.write(resp.content)

app = QApplication(sys.argv)
w = QWidget()
w.setGeometry(100, 100, 600, 450)
w.setWindowTitle("Карта")

pixmap = QPixmap("map.png")
label = QLabel(w)
label.move(0, 0)
label.resize(600, 450)
label.setPixmap(pixmap)

w.show()
sys.exit(app.exec())
