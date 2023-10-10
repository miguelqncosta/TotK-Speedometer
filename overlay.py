
import sys
import datetime

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QMainWindow

import settings

class SpeedometerOverlay(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self.setGeometry(QtCore.QRect(0, 0, settings.overlay_width, settings.overlay_height))
        self.widget = QtWidgets.QWidget()
        self.widget.setStyleSheet('color: white;')
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        current_time = str(datetime.datetime.now().strftime("%H:%M:%S"))
        self.l_time = QtWidgets.QLabel('Time: '+current_time)

        self.l_total = QtWidgets.QLabel('Total')
        self.l_speed = QtWidgets.QLabel('Speed: 0.00 m/s')
        self.l_avg_speed = QtWidgets.QLabel('Avg: 0.00 m/s')
        self.l_max_speed = QtWidgets.QLabel('Max: 0.00 m/s')

        self.l_horizontal = QtWidgets.QLabel('Horizontal')
        self.l_speed_h = QtWidgets.QLabel('Speed: 0.00 m/s')
        self.l_avg_speed_h = QtWidgets.QLabel('Avg: 0.00 m/s')
        self.l_max_speed_h = QtWidgets.QLabel('Max: 0.00 m/s')

        self.l_vertical = QtWidgets.QLabel('Vertical')
        self.l_speed_v = QtWidgets.QLabel('Speed: 0.00 m/s')
        self.l_avg_speed_v = QtWidgets.QLabel('Avg: 0.00 m/s')
        self.l_max_speed_v = QtWidgets.QLabel('Max: 0.00 m/s')

        self.layout.addWidget(self.l_time)
        self.layout.addWidget(self.l_total)
        self.layout.addWidget(self.l_speed)
        self.layout.addWidget(self.l_avg_speed)
        self.layout.addWidget(self.l_max_speed)
        self.layout.addWidget(self.l_horizontal)
        self.layout.addWidget(self.l_speed_h)
        self.layout.addWidget(self.l_avg_speed_h)
        self.layout.addWidget(self.l_max_speed_h)
        self.layout.addWidget(self.l_vertical)
        self.layout.addWidget(self.l_speed_v)
        self.layout.addWidget(self.l_avg_speed_v)
        self.layout.addWidget(self.l_max_speed_v)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def paintEvent(self, event=None):
        painter = QPainter(self)

        painter.setOpacity(0.2)
        painter.setBrush(QColor(0,0,0))
        painter.setPen(QPen(QColor(0,0,0)))
        painter.drawRect(self.rect())

    def update_labels(self, stats):
        current_time = str(datetime.datetime.now().strftime("%H:%M:%S"))
        self.l_time.setText('Time: '+current_time)
        self.l_speed.setText(f'Speed: {stats["total"]["Speed"]:0.2f} m/s')
        self.l_avg_speed.setText(f'Avg: {stats["total"]["Avg"]:0.2f} m/s')
        self.l_max_speed.setText(f'Max: {stats["total"]["Max"]:0.2f} m/s')
        self.l_speed_h.setText(f'Speed: {stats["horizontal"]["Speed"]:0.2f} m/s')
        self.l_avg_speed_h.setText(f'Avg: {stats["horizontal"]["Avg"]:0.2f} m/s')
        self.l_max_speed_h.setText(f'Max: {stats["horizontal"]["Max"]:0.2f} m/s')
        self.l_speed_v.setText(f'Speed: {stats["vertical"]["Speed"]:0.2f} m/s')
        self.l_avg_speed_v.setText(f'Avg: {stats["vertical"]["Avg"]:0.2f} m/s')
        self.l_max_speed_v.setText(f'Max: {stats["vertical"]["Max"]:0.2f} m/s')
        self.widget.setLayout(self.layout)

    def mousePressEvent(self, event):
        sys.exit(0)
