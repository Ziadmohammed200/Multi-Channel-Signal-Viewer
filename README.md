# Multi-Port, Multi-Channel Signal Viewer

## Introduction
Monitoring vital signals is crucial in any ICU room. This project aims to develop a multi-port, multi-channel signal viewer desktop application using Python and Qt, enabling real-time monitoring and analysis of medical signals such as ECG, EMG, and EEG.

---

## Features

### 1. **File Browsing and Signal Management**
- Users can browse their PC to open any signal file.
- Supports three different medical signal types (e.g., ECG, EMG, EEG) with examples of both normal and abnormal signals.

*(Insert image/video of file browsing and signal loading UI)*

### 2. **Real-Time Signal Streaming**
- Connect to a website that emits signals in real time, read the emitted signal, and plot it dynamically.
- Groups must identify unique websites for real-time signal streaming; these websites are allocated on a "first-to-deliver" basis.

*(Insert image/video demonstrating real-time signal streaming)*

### 3. **Graph Configuration**
- Two identical rectangular graphs:
  - Independent signal management for each graph.
  - Option to link graphs to synchronize time frames, signal speed, and viewport (zoom/pan).
  - When unlinked, graphs operate independently.

*(Insert image showing linked/unlinked graph configurations)*

### 4. **Non-Rectangle Graph**
- Includes one non-rectangle graph for cine mode signal visualization. The design and functionality of this graph are unique and signal-specific.

*(Insert image/video of non-rectangle graph in action)*

### 5. **Cine Mode**
- Signals are displayed dynamically in cine mode, mimicking ICU monitors.
- Signals automatically rewind or stop at the end, based on user settings.

*(Insert video of cine mode visualization)*

### 6. **Signal Manipulations**
Users can perform the following manipulations via the UI:
- **Change Color:** Customize signal color.
- **Label/Title:** Add labels or titles to signals.
- **Show/Hide:** Toggle signal visibility.
- **Cine Speed:** Adjust the playback speed.
- **Zoom/Pan:** Zoom in/out and pan in any direction (via mouse or sliders).
- **Pause/Play/Rewind:** Control playback.
- **Boundary Constraints:** Prevent scrolling or panning beyond signal limits.
- **Move Signals:** Transfer signals between graphs seamlessly.

*(Insert image demonstrating signal manipulations and controls)*

### 7. **Signal Glue**
- Cut segments from two signals (one from each graph) and merge them in a third graph using signal interpolation.
- Glue parameters:
  - Window start and size for each signal.
  - Gap (positive distance) or overlap (negative distance) between signals.
  - Interpolation order.

*(Insert image/video of the glue operation process)*

### 8. **Exporting & Reporting**
- Generate a report of the glue operation with:
  - Snapshots of the glued signal.
  - Data statistics (mean, standard deviation, duration, min/max values).
- Export reports to a well-organized PDF (generated programmatically).
- Include tables for statistics and multi-page layouts for multiple signals and snapshots.

*(Insert image of a sample report and statistics table)*

---

## Project Structure

### Directories
- **src/**: Source code.
- **data/**: Sample medical signal files (ECG, EMG, EEG).
- **reports/**: Generated PDF reports.
- **docs/**: Documentation and user guides.

### Files
- **README.md**: Project overview and setup instructions.
- **requirements.txt**: List of dependencies.
- **main.py**: Entry point for the application.
- **glue_utils.py**: Signal glue and interpolation logic.
- **pdf_report.py**: PDF generation logic.
- **real_time_stream.py**: Real-time signal streaming handler.
- **ui_design.ui**: Qt Designer file for UI layout.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/multi-channel-signal-viewer.git
   cd multi-channel-signal-viewer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

---

## Usage

1. **Open Signal Files**:
   - Use the "Browse" button to select signal files.
   *(Insert image showing signal file selection)*

2. **Stream Real-Time Signals**:
   - Connect to a real-time signal website via the provided interface.
   *(Insert video demonstrating real-time signal streaming interface)*

3. **Manipulate Graphs**:
   - Use UI controls to customize the signal display, link/unlink graphs, and adjust cine speed.
   *(Insert image showing graph manipulation controls)*

4. **Glue Signals**:
   - Cut and merge signals using the "Signal Glue" tab.
   *(Insert video showcasing the glue operation)*

5. **Generate Reports**:
   - Export glued signal statistics and snapshots to a PDF via the "Export Report" button.
   *(Insert image showing a generated report preview)*

---

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments
- ICU monitor inspiration for cine mode.
- Contributions from [Team Name/Group].

