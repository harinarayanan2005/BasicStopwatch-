import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QListWidget
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stopwatch")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #282828;")  # Dark background for contrast

        # Stopwatch state
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.is_pomodoro_mode = False
        self.time_format_24hr = True  # Default time format: 24-hour

        # Create UI elements
        self.time_display = QLabel("00:00:00.000", self)
        self.time_display.setStyleSheet("font-size: 30px; color: #f1c40f; font-weight: bold;")

        self.lap_list = QListWidget(self)
        self.lap_list.setStyleSheet("background-color: #34495e; color: white; font-size: 14px;")

        # Buttons for functionality
        self.start_button = QPushButton("Start", self)
        self.start_button.setStyleSheet(self.button_style("#1abc9c", "#16a085", "#1abc9c"))
        self.start_button.clicked.connect(self.toggle_start_pause)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setStyleSheet(self.button_style("#e74c3c", "#c0392b", "#e74c3c"))
        self.reset_button.clicked.connect(self.reset)

        self.lap_button = QPushButton("Lap", self)
        self.lap_button.setStyleSheet(self.button_style("#f39c12", "#f1c40f", "#f39c12"))
        self.lap_button.clicked.connect(self.record_lap)

        # Layout management
        self.main_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()

        self.main_layout.addWidget(self.time_display)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.lap_list)

        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.lap_button)

        # Timer for updating the time display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.is_fullscreen = False  # Track fullscreen state

        # Button to toggle 12/24-hour time format
        self.format_button = QPushButton("Switch Time Format", self)
        self.format_button.setStyleSheet(self.button_style("#9b59b6", "#8e44ad", "#9b59b6"))
        self.format_button.clicked.connect(self.toggle_time_format)
        self.main_layout.addWidget(self.format_button)

        # Progress bar for visual countdown
        self.progress_radius = 100
        self.progress = 0  # Will be used for countdown progress
        self.show()

    def button_style(self, default_color, hover_color, pressed_color):
        return f"""
            QPushButton {{
                background-color: {default_color};
                color: white;
                font-size: 16px;
                border-radius: 12px;
                padding: 12px;
                width: 100px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

    def toggle_start_pause(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.start_button.setText("Start")
            self.timer.stop()
        else:
            self.start_time = time.time()
            self.start_button.setText("Pause")
            self.timer.start(10)
        self.running = not self.running

    def reset(self):
        self.elapsed_time = 0
        self.lap_times.clear()
        self.lap_list.clear()
        self.time_display.setText("00:00:00.000")
        self.start_button.setText("Start")
        self.timer.stop()
        self.running = False

    def record_lap(self):
        lap_time = self.elapsed_time + (time.time() - self.start_time if self.running else 0)
        minutes, seconds = divmod(lap_time, 60)
        seconds, milliseconds = divmod(seconds, 1)
        lap_time_str = f"{int(minutes):02}:{int(seconds):02}:{int(milliseconds*1000):03}"
        self.lap_times.append(lap_time_str)
        self.lap_list.addItem(f"Lap {len(self.lap_times)}: {lap_time_str}")

    def update_time(self):
        if self.running:
            current_time = self.elapsed_time + (time.time() - self.start_time)
        else:
            current_time = self.elapsed_time

        minutes, seconds = divmod(current_time, 60)
        seconds, milliseconds = divmod(seconds, 1)

        # Display the time based on format (12-hour or 24-hour)
        if self.time_format_24hr:
            time_str = f"{int(minutes):02}:{int(seconds):02}:{int(milliseconds*1000):03}"
        else:
            # 12-hour format
            hours, minutes = divmod(int(minutes), 12)
            time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(milliseconds*1000):03}"

        self.time_display.setText(time_str)

        # Update progress for countdown
        if self.is_pomodoro_mode:
            self.progress += 1
            self.update_visual_countdown()

    def toggle_time_format(self):
        self.time_format_24hr = not self.time_format_24hr
        self.update_time()  # Update time display to reflect new format

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_pomodoro_mode:
            self.update_visual_countdown()

    def update_visual_countdown(self):
        """ Visual countdown using a circular progress bar """
        if self.is_pomodoro_mode:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Set color for the progress bar
            painter.setPen(QPen(QColor(46, 204, 113), 10))
            painter.setBrush(QColor(46, 204, 113, 50))

            # Calculate the progress angle based on elapsed time
            angle = 360 * self.progress / 100

            # Draw the circular progress bar
            painter.drawArc(self.width() // 2 - self.progress_radius, self.height() // 2 - self.progress_radius,
                            self.progress_radius * 2, self.progress_radius * 2, 90 * 16, -angle * 16)
            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stopwatch = Stopwatch()
    sys.exit(app.exec_())
