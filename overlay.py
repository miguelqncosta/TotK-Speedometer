
import datetime

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QScreen
from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

import settings


class SpeedometerOverlay(QMainWindow):
    def __init__(self, screen, map_left, map_top, map_width):
        QMainWindow.__init__(self)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if settings.overlay_width is not None:
            self.setGeometry(QRect(0, 0, settings.overlay_width, self.frameGeometry().height()))
        else:
            self.setGeometry(QRect(0, 0, map_width, self.frameGeometry().height()))

        self.widget = QWidget()
        self.widget.setStyleSheet('color: white;')
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("QLabel{font-size: 16pt;}")

        current_time = str(datetime.datetime.now().strftime("%H:%M:%S"))
        self.l_time = QLabel('Time: '+current_time)

        self.l_total = QLabel('Total')
        self.l_total.setStyleSheet("QLabel{font-size: 20pt; padding-top: 1em}")
        self.l_speed = QLabel('Speed: 0.00 m/s')
        self.l_avg_speed = QLabel('Avg: 0.00 m/s')
        self.l_max_speed = QLabel('Max: 0.00 m/s')

        self.l_horizontal = QLabel('Horizontal')
        self.l_horizontal.setStyleSheet("QLabel{font-size: 20pt; padding-top: 1em}")
        self.l_speed_h = QLabel('Speed: 0.00 m/s')
        self.l_avg_speed_h = QLabel('Avg: 0.00 m/s')
        self.l_max_speed_h = QLabel('Max: 0.00 m/s')

        self.l_vertical = QLabel('Vertical')
        self.l_vertical.setStyleSheet("QLabel{font-size: 20pt; padding-top: 1em}")
        self.l_speed_v = QLabel('Speed: 0.00 m/s')
        self.l_avg_speed_v = QLabel('Avg: 0.00 m/s')
        self.l_max_speed_v = QLabel('Max: 0.00 m/s')

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

        self.screen = screen
        # self.center()
        self.move_to_pos(map_left, map_top)


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


    def center(self):
        geo = self.frameGeometry()
        geo.moveCenter(self.screen.geometry().center())
        self.move(geo.topLeft())


    def move_to_pos(self, left, top):
        geo = self.frameGeometry()
        geo.moveCenter(self.screen.geometry().center())
        height = self.frameGeometry().height()
        pos = QPoint(left, top) + QPoint(0, -height)
        self.move(pos)

            
    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()


    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos )
        self.dragPos = event.globalPosition().toPoint()
        event.accept()