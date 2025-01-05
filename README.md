# Multi-Port, Multi-Channel Signal Viewer

## Introduction
Monitoring vital signals is crucial in any ICU room. This project aims to develop a multi-port, multi-channel signal viewer desktop application using Python and Qt, enabling real-time monitoring and analysis of medical signals such as ECG, EMG, and EEG.

---

## Features

### 1. **File Browsing and Signal Management**
- Users can browse their PC to open any signal file.

*(Insert image/video of file browsing and signal loading UI)*

### 2. **Real-Time Signal Streaming**
- Connected to a website that emits radio signals in real time and plot it dynamically.
  

*(Insert image/video demonstrating real-time signal streaming)*

### 3. **Graph Configuration**
- Two identical rectangular graphs:
  - Independent signal management for each graph.
  - Option to link graphs to synchronize time frames, signal speed, and viewport (zoom/pan).
    
*(Insert image showing linked/unlinked graph configurations)*

### 4. **Non-Rectangle Graph**
- Includes one non-rectangle graph for cine mode signal visualization. We plot medical signals in Polar form .

*(Insert image/video of non-rectangle graph in action)*

### 5. **Cine Mode**
- Signals are displayed dynamically in cine mode, mimicking ICU monitors.


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





### Files
- **README.md**: Project overview and setup instructions.
- **requirements.txt**: List of dependencies.
- **task1.py**: Entry point for the application.
- **GluedSignalViewer.py**: Signal glue and interpolation logic.
- **backend_vs_code.py**: Real-time signal streaming handler.
- - **signals/**: Sample medical signal files (ECG, EMG, EEG).

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/your-username/multi-channel-signal-viewer.git](https://github.com/Ziadmohammed200/Signal-Viewer.git](https://github.com/Ziadmohammed200/Signal-Viewer.git)
   cd multi-channel-signal-viewer
   ```



3. **Run the Application**:
   ```bash
   python task1.py
   ```

---

## Usage

1. **Open Signal Files**:
   - Use the "Browse" button to select signal files.
   *(Insert image showing signal file selection)*

2. **Stream Real-Time Signals**:
   - Stream Real-Time Radio Signal .
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
- Contributions from [Team 9].

