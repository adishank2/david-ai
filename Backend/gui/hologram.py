"""
David AI — Desktop Hologram Widget (PyQt5)
A transparent, frameless, Always-On-Top floating widget.
Reacts to David's status by polling the API.
"""
import sys
import math
import time
import requests # pyre-ignore
from PyQt5.QtWidgets import QApplication, QWidget # pyre-ignore
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF # pyre-ignore
from PyQt5.QtGui import QPainter, QColor, QRadialGradient, QPen # pyre-ignore

API_STATUS_URL = "http://127.0.0.1:8001/api/status"


class HologramWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Make transparent, frameless, and always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(200, 200)

        # Drag variables
        self.old_pos = self.pos()
        
        # Animation states
        self.pulse = 0.0
        self.pulse_dir = 1
        self.status = "Idle"
        self.last_status = "Idle"
        
        # Alexa-style Shockwave (Wake Word Trigger)
        self.shockwave_active = False
        self.shockwave_radius = 40
        self.shockwave_alpha = 0
        
        # Timer for animation frame update (60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(16)
        
        # Timer for polling API status (1x per sec)
        self.api_timer = QTimer(self)
        self.api_timer.timeout.connect(self.poll_status)
        self.api_timer.start(500)
    
    def poll_status(self):
        try:
            r = requests.get(API_STATUS_URL, timeout=1)
            if r.status_code == 200:
                data = r.json()
                new_status = data.get("status", "Idle")
                
                # Detect transition into Listening (Wake Word Triggered)
                if new_status == "Listening" and self.status != "Listening":
                    self.shockwave_active = True
                    self.shockwave_radius = 40
                    self.shockwave_alpha = 255
                    
                self.status = new_status
                
        except:
            self.status = "Offline"
    
    def update_animation(self):
        # Determine pulse speed and color based on status
        speed = 0.02
        if "Listening" in self.status:
            speed = 0.08
        elif "Thinking" in self.status or "Speaking" in self.status:
            speed = 0.15
        elif self.status == "Offline":
            speed = 0.01

        self.pulse += speed * self.pulse_dir
        if self.pulse > 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1
        elif self.pulse < 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1
            
        # Update Shockwave
        if self.shockwave_active:
            self.shockwave_radius += 8  # Expand rapidly
            self.shockwave_alpha -= 10  # Fade out
            if self.shockwave_alpha <= 0:
                self.shockwave_active = False
        
        # Trigger repaint
        self.update()

    def get_color(self):
        # Cyan: Idle / Ready
        # Green/Blue: Listening (Alexa-style is Blue, so let's use a bright blue/cyan for Listening)
        # Gold/Orange: Speaking / Thinking
        # Gray: Offline
        
        if "Listening" in self.status:
            return QColor(0, 150, 255) # Alexa Blue
        elif "Thinking" in self.status:
            return QColor(168, 85, 247) # Purple
        elif "Speaking" in self.status:
            return QColor(255, 165, 0) # Gold
        elif self.status == "Offline":
            return QColor(100, 100, 100) # Gray
            
        return QColor(0, 243, 255) # Default Cyan (Idle)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        base_radius = 40
        
        # How much it expands based on the pulse
        anim_offset = self.pulse * 15
        
        current_color = self.get_color()
        
        # Draw outer glow
        glow_radius = base_radius + anim_offset + 20
        gradient = QRadialGradient(center_x, center_y, glow_radius)
        
        glow_color = QColor(current_color)
        glow_color.setAlpha(80) # Semi-transparent
        gradient.setColorAt(0, glow_color)
        
        fade_color = QColor(current_color)
        fade_color.setAlpha(0)
        gradient.setColorAt(1, fade_color)
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(int(center_x), int(center_y)), int(glow_radius), int(glow_radius))
        
        # Draw solid inner core
        core_radius = base_radius + (anim_offset * 0.5)
        painter.setBrush(current_color)
        painter.drawEllipse(QPoint(int(center_x), int(center_y)), int(core_radius), int(core_radius))
        
        # Draw an orbiting ring
        ring_radius = base_radius + 30
        ring_pen = QPen(current_color)
        ring_pen.setWidth(2)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(ring_pen)
        
        # Rotate the ring over time
        angle = (time.time() * 100) % 360
        
        # Save painter state before translation
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(angle)
        painter.drawArc(QRectF(-ring_radius, -ring_radius, ring_radius*2, ring_radius*2), 0, 16 * 270)
        painter.restore()
        
        # Draw Alexa-style Shockwave ring if active
        if self.shockwave_active:
            shock_pen = QPen(QColor(0, 200, 255, max(0, self.shockwave_alpha)))
            shock_pen.setWidth(4)
            painter.setPen(shock_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPoint(int(center_x), int(center_y)), int(self.shockwave_radius), int(self.shockwave_radius))
    
    # Enable dragging the frameless window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()


def run_hologram():
    app = QApplication(sys.argv)
    widget = HologramWidget()
    widget.show()
    # Center it on screen initially
    screen = app.primaryScreen().geometry()
    widget.move(screen.width() - 300, 100) # Top right corner
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_hologram()
