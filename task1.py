import sys
import os
import io
import subprocess
import numpy as np
import pandas as pd
from Demos.FileSecurityTest import sd
# import sounddevice as sd


from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QColorDialog, QMessageBox, QSlider, QLabel, QSizePolicy,
    QGroupBox, QMenu, QLineEdit, QCheckBox, QSpinBox, QMainWindow, QAction,
    QScrollArea, QListWidget, QListWidgetItem, QStyle, QToolButton, QInputDialog,
    QDialog, QTabWidget, QComboBox, QFormLayout, QFrame
)
from PyQt5.QtGui import QIcon, QColor, QCursor
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject, QFileInfo

from GluedSignalViewer import GluedSignalViewer as glueViewer
from matplotlib.widgets import RectangleSelector

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

from scipy.interpolate import interp1d

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image


# from backend_vs_code import stream_audio


def stream_audio(url):
    process = subprocess.Popen(
        ['ffmpeg', '-i', url, '-f', 'wav', '-'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    return process


def plot_audio_signal(audio_process):
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    buffer_size = 1024
    buffer = np.zeros(buffer_size)
    x = np.arange(buffer_size)  # Time points (will be updated)
    line, = ax.plot(x, buffer)
    plt.ylim(-1, 1)
    plt.show()

    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        if indata.shape[0] == buffer_size:
            line.set_ydata(indata[:, 0])
            fig.canvas.draw()
            fig.canvas.flush_events()

    try:
        with sd.InputStream(samplerate=44100, channels=1, callback=audio_callback):
            time_index = 0
            while plt.fignum_exists(fig.number):  # Check if the plot window is still open
                data = audio_process.stdout.read(
                    buffer_size * 2)  # Read buffer_size * 2 bytes to get buffer_size samples
                if not data:
                    break
                audio_data = np.frombuffer(data, dtype=np.int16) / 32768.0
                if audio_data.shape[0] == buffer_size:
                    buffer = np.append(buffer, audio_data)[-buffer_size:]  # Keep the last buffer_size samples
                    time_index += buffer_size

                    # Update the x-axis so that time increases from left to right
                    new_time = np.arange(time_index - buffer_size, time_index)
                    line.set_xdata(new_time)  # Update time points on x-axis
                    line.set_ydata(buffer)  # Update signal values on y-axis
                    ax.set_xlim(time_index - buffer_size, time_index)  # Shift the x-axis
                    fig.canvas.draw()
                    fig.canvas.flush_events()
    except KeyboardInterrupt:
        print("Stream stopped by user")
    finally:
        # Ensure the plot window closes and the audio process is terminated
        audio_process.terminate()  # Stop the ffmpeg process
        audio_process.stdout.close()  # Close the stdout


class BackendVSTab(QWidget):
    def __init__(self, parent=None):
        super(BackendVSTab, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)  # Add spacing between widgets
        self.layout.setContentsMargins(15, 15, 15, 15)  # Add margins around the edges
        self.setLayout(self.layout)

        # Create a title label with styled text
        # title_label = QLabel("Audio Visualization")
        # title_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 18px;
        #         font-weight: bold;
        #         color: #2c3e50;
        #         padding: 5px;
        #     }
        # # """)
        # self.layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Plot container (at the top)
        plot_container = QWidget()
        plot_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        plot_layout = QVBoxLayout(plot_container)

        # Matplotlib figure and canvas
        self.fig, self.ax = plt.subplots(facecolor='white')
        self.fig.set_size_inches(8, 4)  # Set a better default size
        self.canvas = FigureCanvas(self.fig)
        plot_layout.addWidget(self.canvas)

        # Style the plot
        self.ax.set_facecolor('#000000')  # Light gray background
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_xlabel("Time (ms)", fontsize=10, color='#2c3e50')
        self.ax.set_ylabel("Amplitude", fontsize=10, color='#2c3e50')
        self.ax.tick_params(colors='#2c3e50')

        self.layout.addWidget(plot_container)

        # Controls container (at the bottom)
        controls_container = QWidget()
        controls_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setSpacing(10)

        # Status label with improved styling
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        controls_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Play/Stop button with improved styling
        self.play_stop_button = QPushButton("Play")  # start backend vs code
        self.play_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """)
        self.play_stop_button.clicked.connect(self.toggle_backend_vs_code)
        controls_layout.addWidget(self.play_stop_button, alignment=Qt.AlignCenter)

        self.layout.addWidget(controls_container)

        # Timer for updating the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        # Audio process variables
        self.audio_process = None
        self.buffer_size = 1024
        self.buffer = np.zeros(self.buffer_size)
        self.line, = self.ax.plot(np.arange(self.buffer_size), self.buffer, color='#3498db', linewidth=1)
        self.ax.set_ylim(-1, 1)

        # Time index and extended buffer for panning
        self.time_index = 0
        self.full_buffer = np.array([])

        # Initialize panning attributes
        self.panning = False
        self.pan_start = None

        # Connect mouse events
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def toggle_backend_vs_code(self):
        if self.audio_process:
            self.stop_backend_vs_code()
            self.play_stop_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    min-width: 200px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
        else:
            self.run_backend_vs_code()
            self.play_stop_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    min-width: 200px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)

    def run_backend_vs_code(self):
        url = "https://s44.myradiostream.com/9204/listen.mp3"
        self.audio_process = stream_audio(url)
        self.timer.start(10)
        self.status_label.setText("Status: Running")
        self.play_stop_button.setText("Stop")

    def stop_backend_vs_code(self):
        if self.audio_process:
            self.audio_process.terminate()
            self.audio_process.stdout.close()
            self.audio_process = None
        self.timer.stop()
        self.status_label.setText("Status: Stopped")
        self.play_stop_button.setText("Play")

        # After stopping, allow panning and zooming
        self.ax.set_xlim(0, self.time_index)  # Set x-limits to full signal duration
        self.canvas.draw()

    def update_plot(self):
        try:
            data = self.audio_process.stdout.read(self.buffer_size * 2)
            if not data:
                return
            audio_data = np.frombuffer(data, dtype=np.int16) / 32768.0
            self.buffer = np.roll(self.buffer, -len(audio_data))
            self.buffer[-len(audio_data):] = audio_data
            self.line.set_ydata(self.buffer)

            # Update x-axis to create a moving effect
            self.time_index += len(audio_data)
            x_data = np.arange(self.time_index - self.buffer_size, self.time_index)
            self.line.set_xdata(x_data)
            self.ax.set_xlim(x_data[0], x_data[-1])

            # Store the signal history
            self.full_buffer = np.concatenate((self.full_buffer, audio_data))

            self.canvas.draw()
            self.canvas.flush_events()
        except Exception as e:
            print(f"Error updating plot: {e}")

    def on_scroll(self, event):
        """Handle scroll events to show signal history."""
        if event.button == 'up':
            # Scroll back to show history
            self.time_index = max(0, self.time_index - self.buffer_size)
        elif event.button == 'down':
            # Scroll forward
            self.time_index = min(len(self.full_buffer), self.time_index + self.buffer_size)

        # Update the plot with the new time index
        start_index = max(0, self.time_index - self.buffer_size)
        end_index = self.time_index
        x_data = np.arange(start_index, end_index)
        y_data = self.full_buffer[start_index:end_index]

        # Ensure the buffer is filled with zeros if there's not enough history
        if len(y_data) < self.buffer_size:
            y_data = np.pad(y_data, (self.buffer_size - len(y_data), 0), 'constant')

        self.line.set_xdata(x_data)
        self.line.set_ydata(y_data)
        self.ax.set_xlim(x_data[0], x_data[-1])
        self.canvas.draw()

    def on_mouse_press(self, event):
        """Handle mouse press events for panning."""
        if event.button == 1:  # Left mouse button
            self.panning = True
            self.pan_start = event.xdata

    def on_mouse_release(self, event):
        """Handle mouse release events for panning."""
        if event.button == 1:  # Left mouse button
            self.panning = False
            self.pan_start = None

    def on_mouse_move(self, event):
        """Handle mouse move events for panning."""
        if self.panning and event.xdata is not None:
            dx = event.xdata - self.pan_start
            self.pan_start = event.xdata
            self.time_index = int(self.time_index - dx)
            self.time_index = max(0, min(self.time_index, len(self.full_buffer)))

            # Update the plot with the new time index
            start_index = max(0, self.time_index - self.buffer_size)
            end_index = self.time_index
            x_data = np.arange(start_index, end_index)
            y_data = self.full_buffer[start_index:end_index]

            # Ensure the buffer is filled with zeros if there's not enough history
            if len(y_data) < self.buffer_size:
                y_data = np.pad(y_data, (self.buffer_size - len(y_data), 0), 'constant')

            self.line.set_xdata(x_data)
            self.line.set_ydata(y_data)
            self.ax.set_xlim(x_data[0], x_data[-1])
            self.canvas.draw()

    def closeEvent(self, event):
        if self.audio_process:
            self.audio_process.terminate()
            self.audio_process.stdout.close()
        self.timer.stop()
        event.accept()


class Signal:
    """Class to encapsulate individual signal data and plot elements."""

    def __init__(self, name, time, amplitude, color="lime"):
        self.name = name
        self.time = time
        self.amplitude = amplitude
        self.color = color
        self.current_frame = 0
        self.line, = None,
        self.visible = True

    def reset(self):
        """Reset the animation frame."""
        self.current_frame = 0


class CustomToolbar(NavigationToolbar):
    """A custom toolbar that includes additional control buttons."""

    # pause_animation = pyqtSignal()
    # play_animation = pyqtSignal()
    toggle_animation = pyqtSignal()
    change_color = pyqtSignal()
    save_image = pyqtSignal()
    save_pdf = pyqtSignal()
    rewind_animation = pyqtSignal()
    zoom_in_signal = pyqtSignal()
    zoom_out_signal = pyqtSignal()
    reset_zoom_signal = pyqtSignal()
    link_graphs = pyqtSignal()

    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.parent = parent

        # Clear the default toolbar and add custom buttons
        self.clear()
        self.setStyleSheet("QToolBar { border: none; }")

        # # Play Button
        # self.play_btn = QToolButton()
        # self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        # self.play_btn.setToolTip("Play Animation")
        # self.play_btn.clicked.connect(self.play_animation.emit)
        # self.addWidget(self.play_btn)
        #
        # # Pause Button
        # self.pause_btn = QToolButton()
        # self.pause_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        # self.pause_btn.setToolTip("Pause Animation")
        # self.pause_btn.clicked.connect(self.pause_animation.emit)
        # self.addWidget(self.pause_btn)

        # Toggle Play/Pause Button
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.toggle_btn.setToolTip("Play Animation")
        self.toggle_btn.clicked.connect(self.toggle_animation)
        self.addWidget(self.toggle_btn)

        # Rewind Button
        self.rewind_btn = QToolButton()
        self.rewind_btn.setIcon(QIcon("C:icons/replay.png"))
        self.rewind_btn.setToolTip("Rewind Animation")
        self.rewind_btn.clicked.connect(self.rewind_animation.emit)
        self.addWidget(self.rewind_btn)

        # Zoom In Button
        self.zoom_in_btn = QToolButton()
        self.zoom_in_btn.setIcon(QIcon("C:icons/zoomin2.png"))
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in_signal.emit)
        self.addWidget(self.zoom_in_btn)

        # Zoom Out Button
        self.zoom_out_btn = QToolButton()
        self.zoom_out_btn.setIcon(QIcon("C:icons/zoomout.png"))
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out_signal.emit)
        self.addWidget(self.zoom_out_btn)

        # Reset Zoom Button
        self.reset_zoom_btn = QToolButton()
        self.reset_zoom_btn.setIcon(QIcon("C:icons/ZoomReset.png"))
        self.reset_zoom_btn.setToolTip("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom_signal.emit)
        self.addWidget(self.reset_zoom_btn)

        self.label_state = 1
        self.link_label = "icons/1.png"
        self.unlink_label = "icons/2.png"
        self.link_btn = QToolButton()
        self.link_btn.setIcon(QIcon(self.link_label))  # Replace with your icon path
        self.link_btn.setToolTip("Link")
        self.link_btn.clicked.connect(self.link_graphs.emit)
        self.link_btn.clicked.connect(self.change_label)
        self.addWidget(self.link_btn)

        # Save Image Button
        self.save_img_btn = QToolButton()
        self.save_img_btn.setIcon(QIcon("C:icons/save.jpg"))
        self.save_img_btn.setToolTip("Save Image")
        self.save_img_btn.clicked.connect(self.save_image.emit)
        self.addWidget(self.save_img_btn)

        # Save PDF Button
        self.save_pdf_btn = QToolButton()
        self.save_pdf_btn.setIcon(QIcon("C:icons/pdf3.png"))  # Replace with your icon path
        self.save_pdf_btn.setToolTip("Save as PDF")
        self.save_pdf_btn.clicked.connect(self.save_pdf.emit)
        self.addWidget(self.save_pdf_btn)

    def change_label(self):
        if self.label_state == 1:
            self.link_btn.setIcon(QIcon(self.unlink_label))
            self.label_state = 0
        else:
            self.link_btn.setIcon(QIcon(self.link_label))
            self.label_state = 1


class SignalViewer(QWidget):
    """A widget that displays a signal plot with controls."""

    # Signal to request moving the current signal to another viewer
    request_move_signal = pyqtSignal(int)

    def __init__(self, title="Signal Viewer"):
        super().__init__()

        self.setWindowTitle(title)

        #  main layout (vertical layout)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # title input
        title_layout = QHBoxLayout()
        title_label = QLabel("Graph Title:")
        self.title_input = QLineEdit(title)
        self.title_input.setText(title)
        self.title_input.editingFinished.connect(self.update_title)

        # upload button
        self.upload_btn = QPushButton()
        self.upload_btn.setIcon(QIcon("icons/file-upload-icon.webp"))  # Replace with your icon path
        self.upload_btn.setToolTip("Upload Signal")
        self.upload_btn.setText(" Browse")
        self.upload_btn.setMinimumSize(80, 40)
        self.upload_btn.setMaximumSize(300, 60)
        self.upload_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.upload_btn.clicked.connect(self.upload_signal)

        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        title_layout.addWidget(self.upload_btn)
        main_layout.addLayout(title_layout)

        #  plot and controls
        plot_controls_layout = QHBoxLayout()
        main_layout.addLayout(plot_controls_layout)

        #  plot lines (multiple signals)
        self.signals = {}  # Signal instances with unique IDs
        self.next_signal_id = 1  # ID for signals
        self.all_amplitudes = []  # Store amplitudes of all signals for y-axis limit calculation
        self.all_times = []  # Store times of all signals for x-axis limit calculation
        self.data = []  # Store data of all signals

        # Left side: Plot and toolbar
        plot_layout = QVBoxLayout()
        plot_controls_layout.addLayout(plot_layout, stretch=3)
        plot_layout.setContentsMargins(0, 0, 0, 0)

        #  Figure and Canvas
        self.fig = Figure(facecolor='black')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(title, color='white')
        self.ax.set_xlabel("Time (s)", color='white')
        self.ax.set_ylabel("Amplitude (v)", color='white')
        self.ax.set_facecolor('black')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
        self.fig.subplots_adjust(left=0.08, right=0.99, bottom=0.2)

        #  plot line
        self.line, = self.ax.plot([], [], color='lime')

        # Create Canvas
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_layout.addWidget(self.canvas)

        #  Custom Navigation Toolbar
        self.toolbar = CustomToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)

        #  toolbar signals

        # self.toolbar.pause_animation.connect(self.pause_animation)
        # self.toolbar.play_animation.connect(self.play_animation)
        self.toolbar.toggle_animation.connect(self.toggle_animation)
        self.toolbar.save_image.connect(self.save_plot_image)
        self.toolbar.save_pdf.connect(self.save_plot_pdf)
        self.toolbar.rewind_animation.connect(self.rewind_animation)
        self.toolbar.zoom_in_signal.connect(lambda: self.zoom(scale=0.8))
        self.toolbar.zoom_out_signal.connect(lambda: self.zoom(scale=1.25))
        self.toolbar.reset_zoom_signal.connect(self.reset_zoom)
        self.toolbar.link_graphs.connect(self.link)

        # Slider for manual navigation
        slider_layout = QVBoxLayout()
        self.slider_label = QLabel("Navigate Signal:")
        self.slider_label.setStyleSheet("color: black;")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(100)
        slider_layout.addWidget(self.slider_label)
        slider_layout.addWidget(self.slider)
        plot_layout.addLayout(slider_layout)
        self.slider.sliderMoved.connect(self.slider_moved)
        self.last_mouse_x_position = None

        # Right side: Signals List and Controls
        self.controls_layout = QVBoxLayout()
        plot_controls_layout.addLayout(self.controls_layout, stretch=1)

        # Show/Hide Checkbox
        self.show_checkbox = QCheckBox("Show All Signals")
        self.show_checkbox.setChecked(True)
        self.show_checkbox.stateChanged.connect(self.toggle_all_visibility)
        self.controls_layout.addWidget(self.show_checkbox)

        # Playback Speed Control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Playback Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)  # Default speed
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.change_speed)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        self.controls_layout.addLayout(speed_layout)

        # Signal selection ComboBox
        self.signal_selector = QComboBox()
        self.selected_signal_id = None
        self.signal_selector.currentIndexChanged.connect(self.signal_selected)
        self.controls_layout.addWidget(self.signal_selector)

        # Control buttons for selected signal
        self.color_btn = QPushButton("Change Color")
        self.color_btn.clicked.connect(self.change_signal_color)
        self.controls_layout.addWidget(self.color_btn)

        self.visibility_checkbox = QCheckBox("Visible")
        self.visibility_checkbox.setChecked(True)
        self.visibility_checkbox.stateChanged.connect(self.toggle_signal_visibility)
        self.controls_layout.addWidget(self.visibility_checkbox)

        self.move_btn = QPushButton("Move Signal")
        self.move_btn.clicked.connect(self.move_signal)
        self.controls_layout.addWidget(self.move_btn)

        self.clear_btn = QPushButton("Clear Signal")
        self.clear_btn.clicked.connect(self.clear_signal)
        self.controls_layout.addWidget(self.clear_btn)

        # Signal Name Editor
        self.name_editor = QLineEdit()
        self.name_editor.setPlaceholderText("Enter Signal Name")
        self.name_editor.editingFinished.connect(self.update_signal_name)
        self.controls_layout.addWidget(self.name_editor)

        self.controls_layout.addStretch()

        #  animation parameters
        self.color_palette = self.generate_color_palette()
        self.is_paused = False
        self.isLinked = False
        self.window_size = 3
        self.gap = 0
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot)
        self.set_controls_enabled(False)
        self.slider_is_moving = False
        self.panning = False
        self.last_mouse_x_position = None
        self.pan_start = None
        self.selected_start = None
        self.selected_end = None
        self.selector = RectangleSelector(self.ax, self.on_select_segment, useblit=True,
                                          button=[3],  # Left mouse button
                                          interactive=True)

        #  mouse events
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        #  context menu
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.canvas.customContextMenuRequested.connect(self.open_context_menu)

        self.setStyleSheet("background-color: #FAFAFA;")

    def on_select_segment(self, eclick, erelease):
        # Capture start and end x-coordinates from selection
        self.selected_start = eclick.xdata
        self.selected_end = erelease.xdata
        print(f"Selected range: Start={np.round(self.selected_start, 2)}, End={np.round(self.selected_end, 2)}")

    def selected_segment(self):
        return np.round(self.selected_start, 2), np.round(self.selected_end, 2)

    def set_controls_enabled(self, enabled: bool):
        """Enable or disable the signal control buttons based on whether a signal is selected."""
        self.color_btn.setEnabled(enabled)
        self.visibility_checkbox.setEnabled(enabled)
        self.move_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.name_editor.setEnabled(enabled)

    def signal_selected(self):
        """Update the selected signal when the user selects a signal from the ComboBox."""
        current_index = self.signal_selector.currentIndex()
        if current_index >= 0:
            self.selected_signal_id = self.signal_selector.itemData(current_index)
            self.update_signal_controls()
            signal = self.signals[self.selected_signal_id]
            self.name_editor.setText(signal.name)
        else:
            self.selected_signal_id = None
            self.set_controls_enabled(False)

    def update_signal_controls(self):
        """Update control button states based on the selected signal."""
        if self.selected_signal_id is not None and self.selected_signal_id in self.signals:
            signal = self.signals[self.selected_signal_id]
            # Update the color button to match the signal's color
            self.color_btn.setStyleSheet(f"background-color: {signal.color}")
            # Update visibility checkbox to match the signal's visibility
            self.visibility_checkbox.setChecked(signal.visible)
            self.set_controls_enabled(True)
        else:
            # Disable controls if no valid signal is selected
            self.set_controls_enabled(False)

    def add_signal(self, signal: Signal):
        """Add a new signal to the viewer and update the signal selector."""
        signal_id = self.next_signal_id
        self.signals[signal_id] = signal
        self.signal_selector.addItem(signal.name, signal_id)
        self.next_signal_id += 1
        # Automatically select the newly added signal
        self.signal_selector.setCurrentIndex(self.signal_selector.count() - 1)

    def update_signal_name(self):
        """Update the name of the selected signal and refresh the ComboBox and plot legend."""
        if self.selected_signal_id is not None:
            new_name = self.name_editor.text().strip()
            if new_name:
                signal = self.signals[self.selected_signal_id]
                signal.name = new_name

                # Update the ComboBox entry
                current_index = self.signal_selector.currentIndex()
                self.signal_selector.setItemText(current_index, new_name)

                # Update the plot legend
                signal.line.set_label(new_name)
                self.ax.legend(loc='upper right')
                self.canvas.draw()

    def clear_signal(self):
        """Remove a signal based on the selected signal."""
        current_index = self.signal_selector.currentIndex()
        if current_index < 0:
            return
        signal_id = self.signal_selector.itemData(current_index)
        self.clear_signal_by_id(signal_id)
        if self.linker and self.isLinked:
            current_index = self.linker.signal_selector.currentIndex()
            if current_index < 0:
                return
            signal_id = self.linker.signal_selector.itemData(current_index)
            self.linker.clear_signal_by_id(signal_id)

    def generate_color_palette(self):
        """Generate a list of distinct colors for multiple signals."""
        return list(mcolors.TABLEAU_COLORS.keys()) + list(mcolors.CSS4_COLORS.keys())

    def get_unique_color(self):
        """Generate a unique color for each new signal."""
        existing_colors = [signal.color for signal in self.signals.values()]
        for color in self.color_palette:
            if color not in existing_colors:
                return color
        # If all predefined colors are used, generate a random color
        return QColor(np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)).name()

    def change_signal_color(self):
        """Change the color of the selected signal."""
        if self.selected_signal_id is not None:
            signal = self.signals[self.selected_signal_id]
            color = QColorDialog.getColor(initial=QColor(signal.color), parent=self, title="Select Signal Color")
            if color.isValid():
                new_color = color.name()
                signal.color = new_color
                signal.line.set_color(new_color)
                self.color_btn.setStyleSheet(f"background-color: {new_color}")
                self.canvas.draw()

        if self.linker.selected_signal_id is not None:
            signal2 = self.linker.signals[self.linker.selected_signal_id]
            signal2.line.set_color(new_color)
            self.linker.color_btn.setStyleSheet(f"background-color: {new_color}")
            self.linker.canvas.draw()

    def toggle_signal_visibility(self, state):
        """Toggle the visibility of the selected signal."""
        if self.selected_signal_id is not None:
            is_visible = state == Qt.Checked
            signal = self.signals[self.selected_signal_id]
            signal.visible = is_visible
            signal.line.set_visible(is_visible)
            self.canvas.draw()
        if self.linker and self.isLinked:
            is_visible = state == Qt.Checked
            signal = self.linker.signals[self.linker.selected_signal_id]
            signal.visible = is_visible
            signal.line.set_visible(is_visible)
            if not self.visibility_checkbox.isChecked():
                self.linker.visibility_checkbox.setChecked(False)
            else:
                self.linker.visibility_checkbox.setChecked(True)
            self.linker.canvas.draw()

    def clear_signal_by_id(self, signal_id: int):
        """Remove a specific signal from the plot, ComboBox, and UI."""
        if signal_id not in self.signals:
            print(f"Signal ID {signal_id} not found.")
            return

        signal = self.signals[signal_id]
        print(f"Clearing signal: {signal.name}")

        # Remove the signal's line from the plot
        signal.line.remove()

        # Remove the signal from the signals dictionary
        del self.signals[signal_id]

        # Remove the signal from the ComboBox
        for i in range(self.signal_selector.count()):
            if self.signal_selector.itemData(i) == signal_id:
                self.signal_selector.removeItem(i)
                break

        # Update the plot based on remaining signals
        if self.signals:
            try:
                all_amplitudes = np.concatenate([s.amplitude for s in self.signals.values()])
                y_min = np.min(all_amplitudes)
                y_max = np.max(all_amplitudes)
                amp_range = y_max - y_min if y_max != y_min else 1
                self.ax.set_ylim(y_min - 0.1 * amp_range, y_max + 0.1 * amp_range)

                max_x = max(self.window_size, max([len(s.amplitude) for s in self.signals.values()]))
                self.ax.set_xlim(0, max_x)

                # Update the legend
                handles, labels = self.ax.get_legend_handles_labels()

                if any(label and not label.startswith('_') for label in labels):
                    self.ax.legend(loc='upper right')
                else:
                    legend = self.ax.get_legend()
                    if legend:
                        legend.remove()
            except Exception as e:
                QMessageBox.warning(self, "Axis Adjustment Error", f"Failed to adjust axes: {e}")
        else:
            # Clear the axes if no signals remain
            self.ax.clear()
            self.ax.set_xlabel("Time (s)", color='white')
            self.ax.set_ylabel("Amplitude (v)", color='white')
            self.ax.set_ylim(-1, 1)
            self.ax.set_xlim(0, self.window_size)
            self.ax.grid(True)
            self.next_signal_id = self.next_signal_id - 1
            self.slider.setValue(0)
            self.timer.stop()
            self.is_paused = False
            self.fig.subplots_adjust(left=0.085, right=0.97, bottom=0.2)
            self.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Redraw the canvas to reflect changes
        self.canvas.draw()

        # Update slider maximum based on current signals
        self.update_slider_maximum()

    def move_signal(self):
        """Triggered when Move button is clicked to move the selected signal."""
        # Get the selected signal's ID
        current_index = self.signal_selector.currentIndex()
        if current_index < 0:
            QMessageBox.warning(self, "No Selection", "No signal selected to move.")
            return

        signal_id = self.signal_selector.itemData(current_index)
        self.emit_request_move_signal(signal_id)

    def emit_request_move_signal(self, signal_id: int):
        """Emit a signal to move the specified signal to another viewer."""
        self.request_move_signal.emit(signal_id)

    def update_title(self):
        """Update the plot title based on user input."""
        new_title = self.title_input.text()
        self.ax.set_title(new_title, color='white')
        self.canvas.draw()

    # def adjust_timer(self):
    #     """Adjust the timer interval based on the speed slider."""
    #     speed = self.speed_slider.value()
    #     interval = max(1, 100 - speed)  # Map slider value to interval, at least 1 ms
    #     self.timer.setInterval(interval)

    def upload_signal(self):
        """Upload and load signal data from CSV files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Signal Files", "", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )

        if file_paths:
            for file_path in file_paths:
                try:
                    # Load data
                    data = np.genfromtxt(file_path, delimiter=',', skip_header=0)
                    self.data = data

                    if data.ndim == 1:
                        data = data.reshape(-1, 1)  # Ensure 2D array

                    if data.shape[1] < 2:
                        QMessageBox.warning(
                            self, "Invalid Data",
                            f"CSV file '{file_path}' must contain at least two columns: time and amplitude."
                        )
                        continue

                    #  time to start at zero
                    time = data[:, 0] - data[0, 0]
                    amplitude = data[:, 1]

                    self.all_amplitudes.append(amplitude)
                    self.all_times.append(time)

                    #  unique id for the signal
                    signal_id = self.next_signal_id
                    signal_name = os.path.splitext(os.path.basename(file_path))[0]

                    # unique color for the signal
                    color = self.get_unique_color()

                    #  Signal instance
                    signal = Signal(name=signal_name, time=time, amplitude=amplitude, color=color)

                    # Plot the signal with empty data initially
                    line, = self.ax.plot([], [], label=signal.name, color=signal.color)
                    self.ax.legend(loc='upper right')
                    self.canvas.draw()
                    self.signals[signal_id] = signal
                    signal.line = line
                    # Add the new signal
                    self.add_signal(signal)


                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load signal '{file_path}':\n{e}")

            # After all signals are loaded, compute the global min/max amplitude
            if self.all_amplitudes and self.all_times:
                all_amplitudes = np.concatenate(self.all_amplitudes)
                all_times = np.concatenate(self.all_times)

                self.full_x_min = np.min(all_times)
                self.full_x_max = np.max(all_times)
                self.full_y_min = np.min(all_amplitudes)
                self.full_y_max = np.max(all_amplitudes)

                # Compute amplitude range
                amp_range = self.full_y_max - self.full_y_min if self.full_y_max != self.full_y_min else 1

                # Set x-axis limits to fit the entire data range
                self.ax.set_xlim(self.full_x_min, self.full_x_max)

                # Set constant y-axis limits based on full amplitude range
                self.ax.set_ylim(self.full_y_min - 0.1 * amp_range, self.full_y_max + 0.1 * amp_range)

            # Setup the slider for navigating signals
            if self.signals:
                self.slider.setEnabled(True)
                self.update_slider_maximum()
                self.slider.setValue(0)

                # Start animation if not already running
                if not self.timer.isActive():
                    self.timer.start()
                    self.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

            # If more than 2 signals, rewind animation
            if self.next_signal_id > 2:
                self.rewind_animation()

    def update_slider_maximum(self):
        """Update the slider's maximum value based on the longest signal."""
        if self.signals:
            max_length = max([len(s.time) for s in self.signals.values()])
            self.slider.setMaximum(max_length)
        else:
            self.slider.setMaximum(1000)

    def update_plot(self):
        """Update the plot for animation."""
        if not self.signals or self.is_paused or self.slider_is_moving:
            return
        self.fig.subplots_adjust(left=0.085, right=0.97, bottom=0.2)

        updated = False

        for signal in self.signals.values():
            if signal.current_frame < len(signal.time):
                current_time = signal.time[signal.current_frame]
                current_amp = signal.amplitude[signal.current_frame]
                xdata = signal.line.get_xdata()
                ydata = signal.line.get_ydata()
                signal.line.set_data(np.append(xdata, current_time),
                                     np.append(ydata, current_amp))
                signal.current_frame += 1
                updated = True

        if updated:
            # Adjust x-axis to show a moving window based on the latest time across all signals
            latest_time = max([s.time[min(s.current_frame, len(s.time) - 1)] for s in self.signals.values()])
            if latest_time > self.window_size:
                self.ax.set_xlim(latest_time - self.window_size, latest_time)
            else:
                self.ax.set_xlim(0, self.window_size)

            # Restrict Y-axis to the data in the current frame (dynamic Y limits with padding)
            xlim = self.ax.get_xlim()
            visible_signals = [
                s.amplitude[(s.time >= xlim[0]) & (s.time <= xlim[1])] for s in self.signals.values()
            ]

            if visible_signals and any(len(v) > 0 for v in visible_signals):
                visible_y_min = min([v.min() for v in visible_signals if len(v) > 0])
                visible_y_max = max([v.max() for v in visible_signals if len(v) > 0])

                # Add a small padding to the Y limits (e.g., 5% of the range)
                y_range = visible_y_max - visible_y_min
                padding = 0.05 * y_range if y_range > 0 else 0.1  # Ensure minimum padding even for flat signals

                # Set Y-axis limits with padding
                self.ax.set_ylim(visible_y_min - padding, visible_y_max + padding)

            self.canvas.draw()

            # Update slider position based on the maximum current frame
            max_frame = max([s.current_frame for s in self.signals.values()])
            self.slider.setValue(max_frame)

        else:
            # Stop the timer when the animation is complete
            self.timer.stop()

    def toggle_animation(self):
        """Toggle between play and pause for the animation."""
        if self.is_paused:
            # Resume the animation
            self.is_paused = False
            self.timer.start()
            self.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.toolbar.toggle_btn.setToolTip("Pause Animation")
            if self.isLinked and self.linker:
                # Resume the linked viewer as well
                self.linker.is_paused = False
                self.linker.timer.start()
                self.linker.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            # Pause the animation
            self.is_paused = True
            self.timer.stop()
            self.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.toolbar.toggle_btn.setToolTip("Play Animation")
            if self.isLinked and self.linker:
                # Pause the linked viewer as well
                self.linker.is_paused = True
                self.linker.timer.stop()
                self.linker.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def rewind_animation(self):
        """Rewind the animation to the beginning."""
        if self.signals:
            self.is_paused = False
            for signal in self.signals.values():
                signal.reset()
                signal.line.set_data([], [])
            self.ax.set_xlim(0, self.window_size)
            self.ax.set_ylim(*self.ax.get_ylim())
            self.canvas.draw()
            self.slider.setValue(0)
            self.timer.start()

        if self.isLinked and self.linker:
            self.linker.is_paused = False
            for signal in self.linker.signals.values():
                signal.reset()
                signal.line.set_data([], [])
            self.linker.ax.set_xlim(0, self.window_size)
            self.linker.ax.set_ylim(*self.ax.get_ylim())
            self.linker.canvas.draw()
            self.linker.slider.setValue(0)
            self.linker.timer.start()

    def toggle_all_visibility(self, state):
        """Show or hide all signal plots."""
        is_visible = state == Qt.Checked
        for signal in self.signals.values():
            signal.visible = is_visible
            signal.line.set_visible(is_visible)
        self.canvas.draw()
        if self.linker and self.isLinked:
            is_visible = state == Qt.Checked
            print(Qt.Checked)
            for signal in self.linker.signals.values():
                signal.visible = is_visible
                signal.line.set_visible(is_visible)
            if not self.show_checkbox.isChecked():
                self.linker.show_checkbox.setChecked(False)
            else:
                self.linker.show_checkbox.setChecked(True)

            self.linker.canvas.draw()

    def link(self):
        """Toggle the linking between two viewers."""

        if not self.isLinked:
            if self.linker:
                self.rewind_animation()
                self.linker.rewind_animation()
                self.isLinked = True
                self.linker.isLinked = True
                self.linker.toolbar.change_label()
                return True
        else:
            self.isLinked = False
            if self.linker:
                self.linker.isLinked = False
                self.linker.toolbar.change_label()

            return False

    def toggle_visibility(self, state):
        """Show or hide the signal plot."""
        if hasattr(self, 'line'):
            if state == Qt.Checked:
                self.line.set_visible(True)
            else:
                self.line.set_visible(False)
            self.canvas.draw()
        if self.linker and self.isLinked:
            if not self.visibility_checkbox.isChecked():
                self.linker.visibility_checkbox.setChecked(False)
            else:
                self.linker.visibility_checkbox.setChecked(True)
            self.linker.canvas.draw()

    def change_speed(self, value):
        """Change the playback speed based on the speed slider."""
        # Adjust timer interval based on speed slider value
        # Higher speed -> smaller interval
        speed = max(1, value)
        interval = int(100 - speed)
        self.timer.setInterval(interval)
        if self.linker and self.isLinked:
            self.linker.timer.setInterval(interval)
            self.linker.speed_slider.setValue(self.speed_slider.value())

    def save_plot_pdf(self):
        """Save the current plot and statistics as a PDF report."""
        if not self.signals:
            QMessageBox.warning(self, "No Data", "No signals to include in the report.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report as PDF", "Report.pdf", "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            try:
                self.export_report_pdf(file_path, snapshots=1)
            except Exception as e:
                QMessageBox.critical(self, "Save PDF Error", f"Failed to save report as PDF:\n{e}")

    def save_plot_image(self):
        """Save the current plot as an image."""
        if not self.signals:
            QMessageBox.warning(self, "No Data", "No signals to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot as Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        if file_path:
            try:
                self.fig.savefig(file_path, facecolor='black')
                QMessageBox.information(self, "Save Plot", f"Plot saved successfully at:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Plot Error", f"Failed to save plot:\n{e}")

    def slider_moved(self, position):
        """Handle slider movement to navigate the signal."""
        if not self.signals:
            return

        self.slider_is_moving = True

        # For each signal, set the current frame and update the plot
        for signal in self.signals.values():
            frame = min(position, len(signal.time) - 1)
            signal.current_frame = frame
            xdata = signal.line.get_xdata()
            ydata = signal.line.get_ydata()
            new_xdata = signal.time[:frame]
            new_ydata = signal.amplitude[:frame]
            signal.line.set_data(new_xdata, new_ydata)

        # Adjust x-axis to fit the current frame
        if self.signals:
            latest_time = max([s.time[min(s.current_frame, len(s.time) - 1)] for s in self.signals.values()])
            if latest_time > self.window_size:
                self.ax.set_xlim(latest_time - self.window_size, latest_time)
            else:
                self.ax.set_xlim(0, self.window_size)
        self.canvas.draw()

        self.slider_is_moving = False

        if self.linker and self.isLinked:
            for signal in self.linker.signals.values():
                frame = min(position, len(signal.time) - 1)
                signal.current_frame = frame
                xdata = signal.line.get_xdata()
                ydata = signal.line.get_ydata()
                new_xdata = signal.time[:frame]
                new_ydata = signal.amplitude[:frame]
                signal.line.set_data(new_xdata, new_ydata)

            # Adjust x-axis to fit the current frame
            if self.linker.signals:
                latest_time = max([s.time[min(s.current_frame, len(s.time) - 1)] for s in self.linker.signals.values()])
                if latest_time > self.linker.window_size:
                    self.linker.ax.set_xlim(latest_time - self.window_size, latest_time)
                else:
                    self.linker.ax.set_xlim(0, self.window_size)
            self.linker.canvas.draw()

            self.linker.slider_is_moving = False

    def on_scroll(self, event):
        """Zoom in or out based on mouse scroll, including Y-axis zoom functionality."""
        if not self.signals:
            return

        scale_factor = 1.1
        min_x_range = 0.1  # Minimum range for X-axis
        max_x_range = 100  # Maximum range for X-axis
        min_y_range = 0.1  # Minimum range for Y-axis
        max_y_range = 100  # Maximum range for Y-axis

        # Determine zoom direction
        if event.button == 'up':
            scale = 1 / scale_factor  # Zoom in
        elif event.button == 'down':
            scale = scale_factor  # Zoom out
        else:
            return

        # Get current axis limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        # Calculate new width and height
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale

        # Ensure minimum and maximum zoom levels for both axes
        if new_width < min_x_range or new_width > max_x_range:
            new_width = cur_xlim[1] - cur_xlim[0]  # Lock X range if out of bounds
        if new_height < min_y_range or new_height > max_y_range:
            new_height = cur_ylim[1] - cur_ylim[0]  # Lock Y range if out of bounds

        # Get mouse position in data coordinates
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return

        # Calculate relative position of the mouse in X and Y axes
        relx = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
        rely = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])

        # Update X and Y limits
        new_xlim = [
            xdata - new_width * relx,
            xdata + new_width * (1 - relx)
        ]
        new_ylim = [
            ydata - new_height * rely,
            ydata + new_height * (1 - rely)
        ]

        # Clamp X-limits to data bounds
        full_x_min = min([s.time[0] for s in self.signals.values()])
        full_x_max = max([s.time[min(s.current_frame, len(s.time)-1)] for s in self.signals.values()])
        new_xlim[0] = max(full_x_min, new_xlim[0])
        new_xlim[1] = min(full_x_max, new_xlim[1])

        # Clamp Y-limits to visible signal bounds
        visible_signals = [s.amplitude[(s.time >= new_xlim[0]) & (s.time <= new_xlim[1])] for s in self.signals.values()]
        visible_y_min = min([v.min() for v in visible_signals if len(v) > 0], default=cur_ylim[0])
        visible_y_max = max([v.max() for v in visible_signals if len(v) > 0], default=cur_ylim[1])

        # Adjust Y-axis limits based on the current zoom
        new_ylim[0] = max(visible_y_min, new_ylim[0])
        new_ylim[1] = min(visible_y_max, new_ylim[1])

        # Set limits to axes
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Redraw the canvas
        self.canvas.draw()

        # Apply zooming logic to linked plot (if applicable)
        if self.linker and self.isLinked:
            self._apply_zoom_to_linker(scale)

    def on_mouse_press(self, event):
        """Handle mouse press events for panning and context menu."""
        if event.button == 1 and event.inaxes == self.ax:  # Left mouse button
            self.panning = True
            self.pan_start = (event.xdata, event.ydata)  # Starting point of the pan
            self.canvas.setCursor(QCursor(Qt.ClosedHandCursor))
        # elif event.button == 3:  # Right mouse button
        #     self.open_context_menu(event)

    def on_mouse_release(self, event):
        """Handle mouse release events to stop panning."""
        if event.button == 1 and self.panning:  # Left mouse button
            self.panning = False
            self.canvas.setCursor(QCursor(Qt.ArrowCursor))

    def on_mouse_move(self, event):
        """Handle mouse movement for panning."""
        if not self.panning or self.pan_start is None or event.inaxes != self.ax:
            return

        # Get the difference in movement (dx for X-axis, dy for Y-axis)
        dx = self.pan_start[0] - event.xdata
        dy = self.pan_start[1] - event.ydata

        # Update the last mouse position
        self.last_mouse_x_position = event.xdata
        self.last_mouse_y_position = event.ydata

        # Get the current limits of the plot
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        # Calculate new limits based on the pan
        new_xlim = [cur_xlim[0] + dx, cur_xlim[1] + dx]
        new_ylim = [cur_ylim[0] + dy, cur_ylim[1] + dy]

        # Clamp the X-axis limits to the full data bounds
        full_x_min = min([s.time[0] for s in self.signals.values()])
        full_x_max = max([s.time[min(s.current_frame, len(s.time)-1)] for s in self.signals.values()])
        new_xlim[0] = max(full_x_min, new_xlim[0])
        new_xlim[1] = min(full_x_max, new_xlim[1])
        visible_signals = [
            s.amplitude[(s.time >= new_xlim[0]) & (s.time <= new_xlim[1])] for s in self.signals.values()
        ]

        if visible_signals and any(len(v) > 0 for v in visible_signals):
            # Calculate minimum and maximum of visible signal values
            visible_y_min = min([v.min() for v in visible_signals if len(v) > 0])
            visible_y_max = max([v.max() for v in visible_signals if len(v) > 0])

            # Add padding to the Y-limits (e.g., 5% of the range)
            y_range = visible_y_max - visible_y_min
            y_padding = 0.05 * y_range if y_range > 0 else 0.1

            new_y_min = visible_y_min - y_padding
            new_y_max = visible_y_max + y_padding

        # # Clamp the Y-axis limits to the data bounds
        # full_y_min = min([min(s.amplitude) for s in self.signals.values()])
        # full_y_max = max([max(s.amplitude) for s in self.signals.values()])
        new_ylim[0] = max(new_y_min, new_ylim[0])
        new_ylim[1] = min(new_y_max, new_ylim[1])

        # Apply new limits to the axes
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Redraw the canvas to reflect changes
        self.canvas.draw()

        # Apply the same panning logic for the linked plot
        if self.linker and self.isLinked:
            self._apply_panning_to_linker(dx, dy)

    def _apply_panning_to_linker(self, dx, dy):
        """Applies the panning logic to the linked plot."""
        # Get the current limits for the linker
        cur_xlim_linker = self.linker.ax.get_xlim()
        cur_ylim_linker = self.linker.ax.get_ylim()

        # Calculate new limits for the linker
        new_xlim_linker = [cur_xlim_linker[0] + dx, cur_xlim_linker[1] + dx]
        new_ylim_linker = [cur_ylim_linker[0] + dy, cur_ylim_linker[1] + dy]

        # Clamp the X-axis limits to the linker's data bounds
        full_x_min = min([s.time[0] for s in self.linker.signals.values()])
        full_x_max = max([s.time[min(s.current_frame, len(s.time)-1)] for s in self.linker.signals.values()])
        new_xlim_linker[0] = max(full_x_min, new_xlim_linker[0])
        new_xlim_linker[1] = min(full_x_max, new_xlim_linker[1])

        visible_signals = [
            s.amplitude[(s.time >= new_xlim_linker[0]) & (s.time <= new_xlim_linker[1])] for s in self.linker.signals.values()
        ]

        if visible_signals and any(len(v) > 0 for v in visible_signals):
            # Calculate minimum and maximum of visible signal values
            visible_y_min = min([v.min() for v in visible_signals if len(v) > 0])
            visible_y_max = max([v.max() for v in visible_signals if len(v) > 0])

            # Add padding to the Y-limits (e.g., 5% of the range)
            y_range = visible_y_max - visible_y_min
            y_padding = 0.05 * y_range if y_range > 0 else 0.1

            new_y_min = visible_y_min - y_padding
            new_y_max = visible_y_max + y_padding

        # # Clamp the Y-axis limits to the linker's data bounds
        # full_y_min = min([min(s.amplitude) for s in self.linker.signals.values()])
        # full_y_max = max([max(s.amplitude) for s in self.linker.signals.values()])
        new_ylim_linker[0] = max(new_y_min, new_ylim_linker[0])
        new_ylim_linker[1] = min(new_y_max, new_ylim_linker[1])

        # Apply new limits to the linker axes
        self.linker.ax.set_xlim(new_xlim_linker)
        self.linker.ax.set_ylim(new_ylim_linker)

        # Redraw the linker canvas to reflect changes
        self.linker.canvas.draw()


    def _calculate_zoom_limits(self, cur_xlim, cur_ylim, scale, xdata, ydata):
        """Calculate new zoom limits for X and Y axes with bounds and data visibility."""
        # Define minimum and maximum zoom levels
        min_x_range, max_x_range = 0.1, 100  # X-axis range bounds
        min_y_range, max_y_range = 0.1, 100  # Y-axis range bounds

        # Calculate new width and height
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale

        # Enforce minimum and maximum zoom levels
        if new_width < min_x_range or new_width > max_x_range:
            new_width = cur_xlim[1] - cur_xlim[0]  # Lock X range if out of bounds
        if new_height < min_y_range or new_height > max_y_range:
            new_height = cur_ylim[1] - cur_ylim[0]  # Lock Y range if out of bounds

        # Calculate relative zoom centered around the specified data point
        relx = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
        rely = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])

        # Calculate new X and Y limits
        new_xlim = [
            xdata - new_width * relx,
            xdata + new_width * (1 - relx)
        ]
        new_ylim = [
            ydata - new_height * rely,
            ydata + new_height * (1 - rely)
        ]

        # Clamp X limits to data bounds
        full_x_min = min(s.time[0] for s in self.signals.values())
        full_x_max = max(s.time[min(s.current_frame, len(s.time)-1)] for s in self.signals.values())
        new_xlim[0] = max(full_x_min, new_xlim[0])
        new_xlim[1] = min(full_x_max, new_xlim[1])

        # Clamp Y limits based on visible signal bounds
        visible_signals = [
            s.amplitude[(s.time >= new_xlim[0]) & (s.time <= new_xlim[1])]
            for s in self.signals.values()
        ]
        if visible_signals and any(len(v) > 0 for v in visible_signals):
            visible_y_min = min(v.min() for v in visible_signals if len(v) > 0)
            visible_y_max = max(v.max() for v in visible_signals if len(v) > 0)

            # Add padding to Y-limits
            y_range = visible_y_max - visible_y_min
            padding = 0.05 * y_range if y_range > 0 else 0.1

            new_ylim[0] = max(visible_y_min - padding, new_ylim[0])
            new_ylim[1] = min(visible_y_max + padding, new_ylim[1])

        return new_xlim, new_ylim

    def zoom(self, scale=1.0):
        """Zoom the plot by a scale factor centered at the plot center."""
        if not self.signals:
            return

        # Use the last mouse X position or default to the plot center
        if self.last_mouse_x_position is not None:
            center_x = self.last_mouse_x_position
        else:
            center_x = self.get_plot_center()[0]

        # Current plot view limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        # Calculate new limits using the core zoom logic
        new_xlim, new_ylim = self._calculate_zoom_limits(
            cur_xlim, cur_ylim, scale, center_x, (cur_ylim[0] + cur_ylim[1]) / 2
        )

        # Update axes with new limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()

        # Apply zoom to linked plot if applicable
        if self.linker and self.isLinked:
            self._apply_zoom_to_linker(scale)

    def _apply_zoom_to_linker(self, scale):
        """Apply the same zooming logic to the linked plot."""
        if not self.linker or not self.linker.signals:
            return

        # Current plot view limits for the linker
        cur_xlim = self.linker.ax.get_xlim()
        cur_ylim = self.linker.ax.get_ylim()

        # Calculate new limits using the core zoom logic
        center_x = (cur_xlim[0] + cur_xlim[1]) / 2
        center_y = (cur_ylim[0] + cur_ylim[1]) / 2
        new_xlim, new_ylim = self._calculate_zoom_limits(
            cur_xlim, cur_ylim, scale, center_x, center_y
        )

        # Update axes for the linker
        self.linker.ax.set_xlim(new_xlim)
        self.linker.ax.set_ylim(new_ylim)
        self.linker.canvas.draw()

    def reset_zoom(self):
        """Reset zoom to the frame or region where the last zoom or pan was applied."""
        if not self.signals:
            return

        # Use the last mouse X position or default to the current frame's max time
        if hasattr(self, 'last_mouse_x_position') and self.last_mouse_x_position is not None:
            current_time = self.last_mouse_x_position
        else:
            # Fall back to current frame's time if no mouse interaction
            current_frame_times = [s.time[min(s.current_frame, len(s.time) - 1)] for s in self.signals.values()]
            current_time = max(current_frame_times)

        # Calculate new X limits (centered on the current frame or mouse position)
        if current_time > self.window_size / 2:
            new_xlim = (current_time - self.window_size / 2, current_time + self.window_size / 2)
        else:
            new_xlim = (0, self.window_size)

        # Ensure the new X-limits are within the data bounds
        full_x_min = min([s.time[0] for s in self.signals.values()])
        full_x_max = max([s.time[min(s.current_frame, len(s.time) - 1)] for s in self.signals.values()])
        new_xlim = [max(full_x_min, new_xlim[0]), min(full_x_max, new_xlim[1])]

        self.ax.set_xlim(new_xlim)

        # Update Y-limits based on the visible data
        self._update_y_limits(new_xlim)

        self.canvas.draw()

        # Apply the same logic to the linked plot if linked
        if self.linker and self.isLinked:
            self.linker.ax.set_xlim(new_xlim)
            self._update_y_limits(new_xlim, linked=True)
            self.linker.canvas.draw()

    def _update_y_limits(self, xlim, linked=False):
        """Helper function to update Y-axis limits based on visible X-limits."""
        signals = self.linker.signals if linked else self.signals

        visible_signals = [
            s.amplitude[(s.time >= xlim[0]) & (s.time <= xlim[1])] for s in signals.values()
        ]

        if visible_signals and any(len(v) > 0 for v in visible_signals):
            visible_y_min = min([v.min() for v in visible_signals if len(v) > 0])
            visible_y_max = max([v.max() for v in visible_signals if len(v) > 0])

            y_range = visible_y_max - visible_y_min
            padding = 0.05 * y_range if y_range > 0 else 0.1

            self.ax.set_ylim(visible_y_min - padding, visible_y_max + padding)
            if linked:
                self.linker.ax.set_ylim(visible_y_min - padding, visible_y_max + padding)

    def get_plot_center(self):
        """Get the center point of the current plot view."""
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        center = (
            (cur_xlim[0] + cur_xlim[1]) / 2,
            (cur_ylim[0] + cur_ylim[1]) / 2
        )
        return center

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if not self.timer.isActive() and not self.is_paused:
            self.timer.start()

    def get_signal_segment(self, start_time, end_time):
        """Return a segment of the current signal based on start time and window size."""
        data = self.data  # time bta3 awel signal
        filtered_data = data[(data[:, 0] >= start_time) & (data[:, 0] <= end_time)]
        filtered_amplitude = filtered_data[:, 1]
        filtered_time = filtered_data[:, 0]
        return filtered_amplitude, filtered_time


class CustomToolbar2(QWidget):
    def __init__(self, parent=None):
        super(CustomToolbar2, self).__init__(parent)

        # Main layout for the toolbar
        self.layout = QVBoxLayout()

        # Create a GroupBox for buttons
        buttons_group = QGroupBox("Controls")
        buttons_layout = QVBoxLayout()  # Use vertical layout for buttons inside the group box

        # Create buttons
        self.upload_button = QPushButton("Upload")
        self.signal_select = QComboBox()
        self.color_button = QPushButton("Select Color")
        self.play_button = QPushButton("Play")
        self.reset_button = QPushButton("Reset")
        self.delete_button = QPushButton("Delete")

        # Add buttons to the layout
        buttons_layout.addWidget(self.upload_button)
        buttons_layout.addWidget(QLabel("Signal:"))
        buttons_layout.addWidget(self.signal_select)
        buttons_layout.addWidget(self.color_button)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.delete_button)

        # Set layout for the GroupBox
        buttons_group.setLayout(buttons_layout)

        # Add movement speed slider
        slider_group = QGroupBox("Movement Speed")
        slider_layout = QVBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(1)
        slider_label = QLabel("Adjust speed:")
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.speed_slider)
        slider_group.setLayout(slider_layout)

        # Add GroupBoxes to the main layout
        self.layout.addWidget(buttons_group)
        self.layout.addWidget(slider_group)

        # Apply layout to the widget
        self.setLayout(self.layout)

        # Set style for the GroupBox and buttons
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QSlider::groove:horizontal {
                background: #e0e0e0;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #b0b0b0;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QLabel {
                color: #333333;
            }
        """)


class RadarViewer(QWidget):
    def __init__(self, parent=None):
        super(RadarViewer, self).__init__(parent)

        # استخدم تخطيط أفقي
        main_layout = QHBoxLayout()

        # إعداد الرادار
        plt.style.use('default')
        self.figure, self.ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(5, 5))

        self.figure.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        self.ax.grid(color='#cccccc', linestyle='--', alpha=0.7)
        self.ax.spines['polar'].set_color('#cccccc')

        self.ax.set_rmax(20)
        self.ax.set_xticklabels([])
        angles_deg = np.arange(0, 360, 45)
        angles_rad = np.deg2rad(angles_deg)
        radius = 20 * 1.1
        for angle_deg, angle_rad in zip(angles_deg, angles_rad):
            self.ax.text(angle_rad, radius, f'{angle_deg}°',
                         ha='center', va='center',
                         color='#333333', fontsize=10)

        self.ax.tick_params(axis='y', colors='#333333', labelsize=8)

        self.canvas = FigureCanvas(self.figure)

        canvas_frame = QFrame()
        canvas_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_frame.setLayout(canvas_layout)

        # اضف الرادار كـ "تلتين" الشاشة
        main_layout.addWidget(canvas_frame, stretch=2)

        # إعداد الزراير باستخدام CustomToolbar2
        self.toolbar = CustomToolbar2(self)

        # اضف الزراير كـ "تلت" الشاشة
        main_layout.addWidget(self.toolbar, stretch=1)

        # إعداد التخطيط الرئيسي
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # إعداد المؤقت والإشارات
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.signal_data_list = []
        self.current_indices = []
        self.signal_colors = ['#ff4444', '#44ff44', '#4444ff', '#ffaa44', '#ff44ff', '#44ffff',
                              '#ff8888', '#88ff88', '#8888ff', '#ffcc88', '#ff88ff', '#88ffff']
        self.selected_index = -1
        self.movement_speed = 0.001
        self.is_playing = False

        # توصيل الأزرار بالإشارات
        self.toolbar.upload_button.clicked.connect(self.upload_signal)
        self.toolbar.play_button.clicked.connect(self.toggle_play_pause)
        self.toolbar.color_button.clicked.connect(self.select_color)
        self.toolbar.reset_button.clicked.connect(self.reset_movement)
        self.toolbar.delete_button.clicked.connect(self.delete_signal)
        self.toolbar.speed_slider.valueChanged.connect(self.update_speed)
        self.toolbar.signal_select.addItems([])
        self.toolbar.signal_select.currentIndexChanged.connect(self.update_selected_signal)

    def update_toolbar_style(self):
        # Example method to set toolbar colors for light mode
        self.toolbar.setStyleSheet("background-color: #f0f0f0; color: black;")
        for button in self.toolbar.findChildren(QPushButton):
            button.setStyleSheet("background-color: #e0e0e0; color: black;")  # Button colors

    def upload_signal(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Signal File", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            self.load_signal_data(file_name)

    def load_signal_data(self, file_name):
        try:
            data = pd.read_csv(file_name)
            time_data = data.iloc[:, 0].values  # Time column
            voltage_data = data.iloc[:, 1].values  # Voltage column
            self.signal_data_list.append((time_data, voltage_data))
            self.current_indices.append(0)

            # استخدم اسم الملف كاسم الإشارة
            signal_name = file_name.split('/')[-1].split('.')[0]  # يأخذ اسم الملف بدون الامتداد
            self.toolbar.signal_select.addItem(signal_name)  # إضافة اسم الإشارة للقائمة

            self.toolbar.signal_select.setCurrentIndex(len(self.signal_data_list) - 1)  # Update to newly added signal
            self.update_buttons()

            self.start_signal()

        except Exception as e:
            print(f"Error loading signal data: {e}")

    def update_selected_signal(self):
        self.selected_index = self.toolbar.signal_select.currentIndex()
        self.update_buttons()

    def start_signal(self):
        if self.selected_index >= 0:
            print(f"Start signal 1 {self.selected_index}")
            self.timer.start(100)

    def stop_signal(self):
        if self.selected_index >= 0:
            self.timer.stop()

    def toggle_play_pause(self):
        """Toggle between play and pause states"""
        if self.selected_index >= 0:
            if self.is_playing:
                self.timer.stop()
                self.toolbar.play_button.setText("Play")
            else:
                print(f"Start signal 2 {self.selected_index}")
                self.timer.start(100)
                self.toolbar.play_button.setText("Pause")
            self.is_playing = not self.is_playing

    def update_signal(self):
        self.ax.clear()  # Clear previous plot
        self.ax.set_facecolor('white')  # Set axes background color to white

        # Iterate through signal data
        for idx, (time_data, voltage_data) in enumerate(self.signal_data_list):
            current_index = self.current_indices[idx]

            # Ensure current index is within the time_data range
            if current_index < len(time_data):
                # Calculate the angle in radians for polar coordinates
                theta = (time_data[current_index] - time_data[0]) / (time_data[-1] - time_data[0]) * 2 * np.pi

                # Get the signal name from the toolbar dropdown
                signal_name = self.toolbar.signal_select.itemText(idx)
                short_signal_name = signal_name[:5]

                self.ax.plot(theta, voltage_data[current_index], 'o', color=self.signal_colors[idx],
                             label=short_signal_name)

                # If there are previous points, plot the line connecting them
                if current_index > 0:
                    self.ax.plot(np.linspace(0, 2 * np.pi, current_index + 1), voltage_data[:current_index + 1],
                                 color=self.signal_colors[idx])

                # Increment the current index for the next update
                self.current_indices[idx] += 1
            else:
                self.current_indices[idx] = len(voltage_data)  # Reset to the end of voltage data



        # Set title and its color
        self.ax.set_title("Signals Viewer in Polar Coordinates", color='black')  # Title color to black

        # Set limits for the y-axis, ensuring all signals are visible
        self.ax.set_ylim([np.min([v[1] for v in self.signal_data_list]), np.max([v[1] for v in self.signal_data_list])])

        # Set tick colors to black
        self.ax.tick_params(colors='black')  # Set tick mark colors to black

        # Set legend properties (optional)
        legend = self.ax.legend()
        for text in legend.get_texts():
            text.set_color('black')  # Set legend text color to black

        # Draw the updated canvas
        self.canvas.draw()

    def select_color(self):
        if self.selected_index >= 0:
            color = QColorDialog.getColor()
            if color.isValid():
                self.signal_colors[self.selected_index] = color.name()
                print(f"Selected color: {color.name()} for signal {self.selected_index}")

    def update_speed(self):
        if self.selected_index >= 0:
            self.timer.setInterval(int(100 / (self.toolbar.speed_slider.value() or 1)))

    def reset_movement(self):
        self.current_indices = [0] * len(self.signal_data_list)  # Reset index for all signals
        self.ax.clear()
        self.canvas.draw()

    def delete_signal(self):
        if self.selected_index >= 0:
            del self.signal_data_list[self.selected_index]
            del self.current_indices[self.selected_index]
            del self.signal_colors[self.selected_index]
            self.toolbar.signal_select.removeItem(self.selected_index)
            if len(self.signal_data_list) == 0:
                self.selected_index = -1  # Reset the selected index
                self.timer.stop()  # Stop the timer if there are no signals left
                self.ax.clear()
                self.canvas.draw()
            else:
                self.selected_index = self.toolbar.signal_select.currentIndex()
                self.update_buttons()

    def update_buttons(self):
        if self.selected_index >= 0 and self.selected_index < len(self.signal_data_list):
            self.toolbar.play_button.setEnabled(True)
            self.toolbar.color_button.setEnabled(True)
            self.toolbar.reset_button.setEnabled(True)  # Ensure reset button is enabled
            self.toolbar.delete_button.setEnabled(True)  # Ensure delete button is enabled
        else:
            self.toolbar.play_button.setEnabled(False)
            self.toolbar.color_button.setEnabled(False)
            self.toolbar.reset_button.setEnabled(False)  # Ensure reset button is disabled
            self.toolbar.delete_button.setEnabled(False)  # Ensure delete button is disabled


class MainWindow(QMainWindow):
    """Main application window containing two SignalViewer instances."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.viewer_glued = None
        self.setWindowTitle("Signal Viewer Application")
        self.setGeometry(100, 100, 1200, 800)

        self.glued_signal = []
        self.is_glued = False
        self.start1 = 0
        self.end1 = 0
        self.start2 = 0
        self.end2 = 0
        self.gap = 0
        self.segment1 = []
        self.segment2 = []
        self.interpolation_order = None

        # Create a QTabWidget
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Create the first tab for signal viewers
        signal_viewers_widget = QWidget()  # Create a new widget for the first tab
        self.tab_widget.addTab(signal_viewers_widget, "Signal Viewers")

        # Create layout for the signal viewers
        signal_viewers_layout = QVBoxLayout(signal_viewers_widget)

        # Create two SignalViewer instances
        self.viewer1 = SignalViewer(title="Signal Viewer 1")
        self.viewer2 = SignalViewer(title="Signal Viewer 2")
        self.viewer_glued = SignalViewer(title="Glued Signal Viewer")  # Third viewer for glued signal
        self.viewer1.linker = self.viewer2
        self.viewer2.linker = self.viewer1

        # Add both viewers to the layout
        signal_viewers_layout.addWidget(self.viewer1)
        signal_viewers_layout.addWidget(self.viewer2)

        # Create Backend VS Code tab
        self.radar_signal_tab = QWidget()
        self.tab_widget.addTab(self.radar_signal_tab, "Non-rectange & Realtime")

        # Create the layout for the Radar Signal tab (Horizontal Layout)
        radar_signal_layout = QVBoxLayout(self.radar_signal_tab)

        # Create RadarViewer and BackendVSTab instances
        self.radar_viewer = RadarViewer()  # Radar viewer widget
        self.backend_vs_tab = BackendVSTab()  # Backend VS tab widget

        # Add both widgets to the layout
        radar_signal_layout.addWidget(self.radar_viewer)  # Add RadarViewer
        radar_signal_layout.addWidget(self.backend_vs_tab)  # Add BackendVSTab

        # Set the layout for the Radar Signal tab
        self.radar_signal_tab.setLayout(radar_signal_layout)
        # Optional: Set window icon and adjust size
        self.setWindowIcon(QIcon("icons/Signal.png"))  # Update path as needed
        self.resize(1400, 1000)

        self.toolbar = self.addToolBar("Tools")

        self.glue_button = QPushButton("Glue Signals")
        self.viewer1.controls_layout.addWidget(self.glue_button)
        self.viewer_glued = glueViewer()

        self.viewer_glued.gap_changed.connect(self.update_gap)
        self.viewer_glued.interpolation_changed.connect(self.update_gap)

        # Connect glue button to open the glue parameters dialog
        self.glue_button.clicked.connect(self.open_glue_dialog)
        self.glue_button.clicked.connect(self.delete_selected_region)

        # Connect move signals if needed
        self.viewer1.request_move_signal.connect(
            lambda signal_id: self.move_signal_by_id(signal_id, self.viewer1, self.viewer2)
        )
        self.viewer2.request_move_signal.connect(
            lambda signal_id: self.move_signal_by_id(signal_id, self.viewer2, self.viewer1)
        )

    def open_glue_dialog(self):
        try:
            start1, end1 = self.viewer1.selected_segment()
            start2, end2 = self.viewer2.selected_segment()

            self.start1 = start1  # start time of the first signal
            self.end1 = end1  # end time of the first signal
            self.start2 = start2  # start time of the second signal
            self.end2 = end2  # end time of the second signal
            self.kind = 1

            signal1_segment, signal1_time = self.viewer1.get_signal_segment(start1, end1)
            signal2_segment, signal2_time = self.viewer2.get_signal_segment(start2, end2)
            self.segment1 = signal1_segment
            self.segment2 = signal2_segment
            self.time1 = signal1_time
            self.time2 = signal2_time
            print("67")
            self.viewer_glued.assign_segments(self.segment1, self.segment2)

            print("69")

            glued_signal = self.concatenate_signals()
            glued_window = QMainWindow(self)
            print("vghhg")
            self.viewer_glued.assign_glued_signal(glued_signal)
            self.viewer_glued.plot()
            glued_window.setWindowTitle("Glued Signal Viewer")
            glued_window.setCentralWidget(self.viewer_glued)
            glued_window.resize(1000, 600)
            glued_window.show()
        except:
            self.show_message_box("You Should Upload Signal or Select a region")

    def delete_selected_region(self):
        self.viewer1.selector.clear()
        self.viewer2.selector.clear()

    def update_gap(self, gap):
        if not isinstance(gap, str):
            self.gap = gap
        interpolation_map = {"Linear": 1, "Quadratic": 2, "Cubic": 3}
        self.interpolation_order = interpolation_map.get(self.viewer_glued.interpolation_method, 1)
        print(self.interpolation_order)
        glued_signal = self.concatenate_signals()
        self.viewer_glued.assign_glued_signal(glued_signal)
        self.viewer_glued.plot()

    def concatenate_signals(self):
        if self.gap > 0:
            time2 = self.time2 + self.time1[len(self.time1) - 1] + self.gap
            concatenated_x_time = np.concatenate([self.time1, time2])
            concatenated_y_amplitude = np.concatenate([self.segment1, self.segment2])
            glued_signal_interpolated = self.fit_curve(concatenated_x_time, concatenated_y_amplitude, time2)
            glued_signal = np.concatenate([self.segment1, glued_signal_interpolated, self.segment2])

        elif self.gap < 0:
            overlap_length = abs(self.gap)
            overlap1 = self.segment1[-overlap_length:]
            overlap2 = self.segment2[:overlap_length]
            blended_overlap = self.blend_overlap(overlap1, overlap2)
            glued_signal = np.concatenate([self.segment1[:-overlap_length], blended_overlap, self.segment2])

        else:
            # No gap: Directly concatenate the signals
            glued_signal = np.concatenate([self.segment1, self.segment2])

        return glued_signal

    def fit_curve(self, data_point_x, data_points_y, time2):
        polynomial_coefficients = np.polyfit(data_point_x, data_points_y, self.interpolation_order)
        new_data_x = np.linspace(self.time1[-1], time2[0], int(time2[0] - self.time1[-1]))
        new_data_y = np.polyval(polynomial_coefficients, new_data_x)
        return new_data_y

    def blend_overlap(self, overlap1, overlap2):
        """Blend two overlapping regions using weighted averaging."""
        overlap_length = len(overlap1)
        weights = np.linspace(0, 1, overlap_length)
        return (1 - weights) * overlap1 + weights * overlap2

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Error')
        msg.setWindowIcon(QIcon('C:/Users/DELL/PycharmProjects/Signal-Viewer/icons/W.png'))
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def move_signal_by_id(self, signal_id: int, source_viewer: SignalViewer, target_viewer: SignalViewer):
        """Move signal data from source_viewer to target_viewer."""
        if signal_id not in source_viewer.signals:
            QMessageBox.warning(self, "No Data", "Selected signal does not exist.")
            return

        signal = source_viewer.signals[signal_id]

        # Remove signal from source viewer
        source_viewer.clear_signal_by_id(signal_id)

        # Add signal to target viewer
        print(f"id before : {target_viewer.next_signal_id}")
        # signal.name=f"Signal {target_viewer.next_signal_id}"
        target_viewer.signals[target_viewer.next_signal_id] = signal
        # signal.color=target_viewer.get_unique_color()

        # Plot the signal in the target viewer
        line, = target_viewer.ax.plot([], [], label=signal.name, color=signal.color)
        signal.line = line
        target_viewer.ax.legend(loc='upper right')
        target_viewer.canvas.draw()

        # Add the signal to the ComboBox in the target viewer
        target_viewer.add_signal(signal)
        # target_viewer.signal_selector.addItem(signal.name, target_viewer.next_signal_id)

        print(f"id after : {target_viewer.next_signal_id}")

        # Update y-axis limits in target viewer
        if target_viewer.signals:
            all_amplitudes = np.concatenate([s.amplitude for s in target_viewer.signals.values()])
            y_min = np.min(all_amplitudes)
            y_max = np.max(all_amplitudes)
            amp_range = y_max - y_min if y_max != y_min else 1
            target_viewer.ax.set_ylim(y_min - 0.1 * amp_range, y_max + 0.1 * amp_range)
            target_viewer.ax.set_xlim(0, target_viewer.window_size)
            target_viewer.canvas.draw()

        # Update slider maximum in target viewer
        target_viewer.update_slider_maximum()
        target_viewer.rewind_animation()
        target_viewer.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        # Start animation in target viewer if not already running
        if not target_viewer.timer.isActive():
            target_viewer.timer.start()
            target_viewer.toolbar.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        QMessageBox.information(self, "Move Signal", f"Signal '{signal.name}' moved successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())