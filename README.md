# Multi-Port, Multi-Channel Signal Viewer

## Introduction
Monitoring vital signals is crucial in any ICU room. This project aims to develop a multi-port, multi-channel signal viewer desktop application using Python and Qt, enabling real-time monitoring and analysis of medical signals such as ECG, EMG, and EEG.

---

## Features

### 1. **File Browsing and Signal Management**
- Users can browse their PC to open any signal file.

![File Browsing UI](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/browse.png)

### 2. **Graph Configuration**
- Two identical rectangular graphs:
  - Independent signal management for each graph.
  - Option to link graphs to synchronize time frames, signal speed, and viewport (zoom/pan).

![Graph Configuration](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/viewers.png)

### 3. **Real-Time Signal Streaming**
- Connected to a website that emits radio signals in real time and plots them dynamically.

![Real-Time Signal Streaming](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/streaming.png)

### 4. **Non-Rectangle Graph**
- Includes one non-rectangle graph for cine mode signal visualization. Medical signals are plotted in polar form.

![Non-Rectangle Graph](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/nonrectangularandreal.png)

### 5. **Cine Mode**
- Signals are displayed dynamically in cine mode, mimicking ICU monitors.

![Cine Mode Visualization](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/cinemode.png)

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

![Signal Manipulations](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/changecolor.png)

![Cine Speed Control](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/changespeed.png)

### 7. **Signal Glue**
- Cut segments from two signals (one from each graph) and merge them in a third graph using signal interpolation.
- Glue parameters:
  - Window start and size for each signal.
  - Gap (positive distance) or overlap (negative distance) between signals.
  - Interpolation order.

![Signal Glue Operation](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/glue.png)

### 8. **Exporting & Reporting**
- Generate a report of the glue operation with:
  - Snapshots of the glued signal.
  - Data statistics (mean, standard deviation, duration, min/max values).
- Export reports to a well-organized PDF (generated programmatically).
- Include tables for statistics and multi-page layouts for multiple signals and snapshots.

![Exported Report Sample](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/report.png)

---

## Project Structure

### Files
- **README.md**: Project overview and setup instructions.
- **requirements.txt**: List of dependencies.
- **task1.py**: Entry point for the application.
- **GluedSignalViewer.py**: Signal glue and interpolation logic.
- **backend_vs_code.py**: Real-time signal streaming handler.
- **signals/**: Sample medical signal files (ECG, EMG, EEG).

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Ziadmohammed200/Signal-Viewer.git
   cd Signal-Viewer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python task1.py
   ```

---

## Usage

1. **Open Signal Files**:
   - Use the "Browse" button to select signal files.
   
     ![File Selection](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/browse.png)

2. **Stream Real-Time Signals**:
   - Stream real-time radio signals.

     ![Real-Time Streaming](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/streaming.png)

3. **Manipulate Graphs**:
   - Use UI controls to customize the signal display, link/unlink graphs, and adjust cine speed.

     ![Graph Manipulation Controls](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/changespeed.png)

4. **Glue Signals**:
   - Cut and merge signals using the "Signal Glue" tab.

     ![Glue Operation](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/glue.png)

5. **Generate Reports**:
   - Export glued signal statistics and snapshots to a PDF via the "Export Report" button.

     ![Generated Report Preview](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/report.png)

---

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments
- ICU monitor inspiration for cine mode.
- Contributions from [Team 9].

