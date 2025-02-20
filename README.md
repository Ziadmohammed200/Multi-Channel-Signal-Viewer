# Multi-Port, Multi-Channel Signal Viewer

## Introduction
Monitoring vital signals is crucial in any ICU room. This project aims to develop a multi-port, multi-channel signal viewer desktop application using Python and Qt, enabling real-time monitoring and analysis of medical signals such as ECG, EMG, and EEG.

---

## Features

### 1. **File Browsing and Signal Management**
- Users can browse their PC to open any signal file.



### 2. **Graph Configuration**
- Two identical rectangular graphs:
  - Independent signal management for each graph.
  - Option to link graphs to synchronize time frames, signal speed, and viewport (zoom/pan).

![Graph Configuration](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/viewers.png)

### 3. **Real-Time Signal Streaming**
- Connected to a website that emits radio signals in real time and plots them dynamically.

### 4. **Non-Rectangle Graph**
- Includes one non-rectangle graph for cine mode signal visualization. Medical signals are plotted in polar form.

![Non-Rectangle Graph](https://github.com/Ziadmohammed200/Signal-Viewer/blob/c2e0ff803b3f8a175e33c285577219df036697ce/images/nonrectangularandreal.png)

### 5. **Cine Mode**
- Signals are displayed dynamically in cine mode, mimicking ICU monitors.



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

![Signal Glue Operation](https://github.com/Ziadmohammed200/Multi-Channel-Signal-Viewer/blob/d1f3cccfff5477b925553d7897f7faa2daff6dc5/images/glue1.png)
![Signal Glue Operation2](https://github.com/Ziadmohammed200/Multi-Channel-Signal-Viewer/blob/d1f3cccfff5477b925553d7897f7faa2daff6dc5/images/glue2.png)
### 8. **Exporting & Reporting**
- Generate a report of the glue operation with:
  - Snapshots of the glued signal.
  - Data statistics (mean, standard deviation, duration, min/max values).
- Export reports to a well-organized PDF (generated programmatically).
- Include tables for statistics and multi-page layouts for multiple signals and snapshots.
 ![Signal Glue Snaps](https://github.com/Ziadmohammed200/Multi-Channel-Signal-Viewer/blob/a88655416ef3c4653b1eb8c07bf7c2c1d64e129a/snapshot_1.png)


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
   
    

2. **Stream Real-Time Signals**:
   - Stream real-time radio signals.

     

3. **Manipulate Graphs**:
   - Use UI controls to customize the signal display, link/unlink graphs, and adjust cine speed.

     
4. **Glue Signals**:
   - Cut and merge signals using the "Signal Glue" tab.

    
5. **Generate Reports**:
   - Export glued signal statistics and snapshots to a PDF via the "Export Report" button.

     
---

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments
- ICU monitor inspiration for cine mode.
## Contributors
- [Ziad Mohamed](https://github.com/Ziadmohammed200) 
- [Marcilino Adel](https://github.com/marcilino-adel)
- [Ahmed Etman](https://github.com/AhmedEtma)
- [Pavly Awad](https://github.com/PavlyAwad)

