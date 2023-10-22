
import datetime

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

import settings


class SpeedometerOverlay(QMainWindow):
    def __init__(self, map_left, map_top, map_width):
        QMainWindow.__init__(self)
        self.map_left = map_left
        self.map_top = map_top
        self.map_width = map_width
        self.was_dragged = False

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setContentsMargins(40,40,40,40)

        # Close button
        self.close_button = QPushButton('X', self.widget)
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.quit)
        self.close_button.setStyleSheet(settings.close_button_style)
        self.close_button.setGeometry(self.widget.width() - 30, 0, 30, 30)

        # Labels
        current_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
        self.l_time = QLabel('Time: '+current_time)
        self.l_total = QLabel('Total')
        self.l_speed = QLabel(f'Speed: {0.0:0.2f} {settings.units[1]}')
        self.l_avg_speed = QLabel(f'Avg: {0.0:0.2f} {settings.units[1]}')
        self.l_max_speed = QLabel(f'Max: {0.0:0.2f} {settings.units[1]}')
        self.l_horizontal = QLabel('Horizontal')
        self.l_speed_h = QLabel(f'Speed: {0.0:0.2f} {settings.units[1]}')
        self.l_avg_speed_h = QLabel(f'Avg: {0.0:0.2f} {settings.units[1]}')
        self.l_max_speed_h = QLabel(f'Max: {0.0:0.2f} {settings.units[1]}')
        self.l_vertical = QLabel('Vertical')
        self.l_speed_v = QLabel(f'Speed: {0.0:0.2f} {settings.units[1]}')
        self.l_avg_speed_v = QLabel(f'Avg: {0.0:0.2f} {settings.units[1]}')
        self.l_max_speed_v = QLabel(f'Max: {0.0:0.2f} {settings.units[1]}')

        # Stylesheets
        self.l_time.setStyleSheet(settings.text_style_ok)
        self.l_total.setStyleSheet(settings.title_style)
        self.l_horizontal.setStyleSheet(settings.title_style)
        self.l_vertical.setStyleSheet(settings.title_style)
        self.widget.setStyleSheet(settings.text_style_ok)

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
        self.reposition()


    def update_labels(self, stats, text_style):
        self.widget.setStyleSheet(text_style)
        current_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
        self.l_time.setText('Time: '+current_time)

        if stats is not None:
            self.l_speed.setText(f'Speed: {stats["total"]["Speed"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_avg_speed.setText(f'Avg: {stats["total"]["Avg"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_max_speed.setText(f'Max: {stats["total"]["Max"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_speed_h.setText(f'Speed: {stats["horizontal"]["Speed"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_avg_speed_h.setText(f'Avg: {stats["horizontal"]["Avg"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_max_speed_h.setText(f'Max: {stats["horizontal"]["Max"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_speed_v.setText(f'Speed: {stats["vertical"]["Speed"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_avg_speed_v.setText(f'Avg: {stats["vertical"]["Avg"]*settings.units[0]:0.2f} {settings.units[1]}')
            self.l_max_speed_v.setText(f'Max: {stats["vertical"]["Max"]*settings.units[0]:0.2f} {settings.units[1]}')


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(settings.overlay_opacity)
        painter.setBrush(QColor(*settings.overlay_color))
        painter.setPen(QPen(QColor(*settings.overlay_color)))
        painter.drawRoundedRect(self.rect(), 10, 10)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.close_button.setGeometry(self.widget.width() - 30, 0, 30, 30)
        if not self.was_dragged:
            self.reposition()


    def reposition(self):
        height = self.frameGeometry().height()
        width = self.frameGeometry().width()
        offset =  QPoint(settings.horizontal_offset, - settings.vertical_offset)
        map_pos =  QPoint(self.map_left, self.map_top)
        pos = map_pos + offset + QPoint(self.map_width/2 - width/2, - height)
        self.move(pos)


    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()


    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos )
        self.dragPos = event.globalPosition().toPoint()
        self.was_dragged = True
        event.accept()


    def set_runnable(self, runnable):
        self.runnable = runnable


    def quit(self):
        self.runnable.stop()
        self.runnable.wait()
        self.close()
