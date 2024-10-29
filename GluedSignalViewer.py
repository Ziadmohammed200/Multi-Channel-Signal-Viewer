from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QGroupBox, QFormLayout, QWidget, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class GluedSignalViewer(QWidget):
    gap_changed = pyqtSignal(int)
    interpolation_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GluedSignalViewer")
        self.setWindowIcon(QIcon("path_to_icon.png"))  # Add a valid path for the icon
        self.figure = plt.Figure(facecolor='black')
        self.resize(1000, 600)
        self.axis = self.figure.add_subplot(111)

        # Set up plot appearance
        self.axis.set_facecolor('black')
        self.axis.set_xlabel('Time (s)', color='white')
        self.axis.set_ylabel('Amplitude', color='white')
        self.axis.tick_params(axis='x', colors='white')
        self.axis.tick_params(axis='y', colors='white')
        self.axis.grid(True, which='both', linestyle='-', linewidth=0.5, color='white')

        # Create layout
        vertical_layout = QVBoxLayout()

        # Create a canvas for the plot
        self.canvas = FigureCanvas(self.figure)
        vertical_layout.addWidget(self.canvas)

        # Slider section with label
        self.group = QGroupBox("Adjustments")
        self.form = QFormLayout()

        self.slider_label = QLabel("Gap Adjustment: 0")
        self.moving_slider = QSlider(Qt.Horizontal)
        self.moving_slider.setRange(-50, 50)
        self.moving_slider.setTickInterval(1)
        self.moving_slider.setTickPosition(QSlider.TicksBelow)
        self.moving_slider.sliderMoved.connect(self.update_slider_value)
        self.moving_slider.valueChanged.connect(self.slider_value)

        self.form.addRow(self.slider_label, self.moving_slider)

        # Dropdown list for interpolation method selection
        self.interpolation_dropdown = QComboBox()
        self.interpolation_dropdown.addItems(["Linear", "Quadratic", "Cubic"])
        self.interpolation_dropdown.currentTextChanged.connect(self.update_interpolation_method)
        self.interpolation_dropdown.setFixedWidth(150)
        self.form.addRow(QLabel("Interpolation Method:"), self.interpolation_dropdown)

        self.group.setLayout(self.form)
        vertical_layout.addWidget(self.group)

        # "Generate Report" button
        self.report_button = QPushButton("Generate Report")
        self.report_button.clicked.connect(self.generate_report)
        vertical_layout.addWidget(self.report_button)

        self.setLayout(vertical_layout)

        self.glued_signal = []
        self.interpolation_method = "Linear"  # Default interpolation method

    def assign_glued_signal(self, glued_signal):
        self.glued_signal = glued_signal

    def plot(self):
        """Plot the glued signal with proper axis settings."""
        self.axis.clear()

        # Reapply axis settings
        self.axis.set_facecolor('black')
        self.axis.set_xlabel('Time (s)', color='white')
        self.axis.set_ylabel('Amplitude', color='white')
        self.axis.tick_params(axis='x', colors='white')
        self.axis.tick_params(axis='y', colors='white')
        self.axis.grid(True, which='both', linestyle='-', linewidth=0.5, color='white')

        # Create time array and plot the glued signal
        time_array = np.arange(len(self.glued_signal)) / 100
        self.axis.plot(time_array, self.glued_signal, color='white')
        self.canvas.draw()

    def update_slider_value(self, value):
        """Update the slider label dynamically."""
        self.slider_label.setText(f"Gap Adjustment: {value}")

    def slider_value(self, value):
        """Emit gap_changed signal with slider value."""
        self.gap_changed.emit(value)

    def update_interpolation_method(self, method):
        """Update interpolation method and emit signal when changed."""
        self.interpolation_method = method
        self.interpolation_changed.emit(method)

    def save_signal_plot(self):
        """Save a plot of the glued signal as an image."""
        plt.figure(figsize=(8, 4))
        time_array = np.arange(len(self.glued_signal)) / 1000
        plt.plot(time_array, self.glued_signal, color='blue')
        plt.title("Glued Signal")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.savefig("glued_signal_snapshot.png", bbox_inches='tight')
        plt.close()

    def generate_report(self):
        """Generate a PDF report for the glued signal."""
        try:
            self.save_signal_plot()
            pdf_filename = "glued_signal_report.pdf"
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Title with center alignment
            title = Paragraph("Glued Signal Report", styles["Title"])
            elements.append(title)
            elements.append(Spacer(1, 0.25 * inch))

            # Subtitle
            subtitle = Paragraph(
                "This report provides an analysis of the glued signal, including statistics and a visual representation.",
                styles["BodyText"])
            elements.append(subtitle)
            elements.append(Spacer(1, 0.25 * inch))

            # Image section
            image_path = "glued_signal_snapshot.png"
            if os.path.exists(image_path):
                img = ReportLabImage(image_path, width=5 * inch, height=3 * inch)
                img.hAlign = "CENTER"
                elements.append(img)
            else:
                QMessageBox.warning(self, "Image Not Found", f"Could not find image at {image_path}")

            # Save the report
            doc.build(elements)
            QMessageBox.information(self, "Report Generated", f"Report saved as {pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the report: {str(e)}")

