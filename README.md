# Multi-Port, Multi-Channel Signal Viewer
This repository contains a desktop application for a multi-port, multi-channel signal viewer developed in Python using Qt. The primary objective is to monitor and analyze vital signals in real-time, with applications in critical care, such as ICU monitoring.

Features
Signal Management
File Browsing: Users can load any signal file from their computer. Each signal type is categorized into multiple groups, including:
ECG (Electrocardiogram)
EMG (Electromyogram)
EEG (Electroencephalogram)
Real-Time Data Streaming: Ability to connect to websites that emit real-time signal data, read the data, and visualize it.
Graph Display
Dual Graphs: Displays two identical graphs, each capable of showing different signals or the same one. Users can control both graphs independently or link them to synchronize time frames, speeds, and viewports.
Non-Rectangular Graph Option: Users can select a non-rectangular shape for displaying signals in "cine mode," emulating continuous, real-time signal streaming.
Cine Mode for Signal Viewing
Real-Time Signal Playback: Signals appear in cine mode, emulating the continuous data flow seen in ICU monitors.
Rewind and Playback Options: Users can rewind and replay signals when they reach the end, allowing continuous analysis without reloading the file.
Interactive Controls
Users can interact with and customize the signals displayed using several UI elements:

Color, Label, and Title Customization: Change the appearance and labeling of signals.
Visibility Controls: Show or hide specific signals on the graph.
Scrolling and Panning: Scroll or pan in any direction (left, right, top, bottom) with the help of sliders and pan gestures.
Graph Manipulation: Move signals across graphs, zoom in/out, control playback speed, and use pause/play/rewind options.
Signal Glue
Segment Selection and Interpolation: Allows users to select two segments from any two signals, glue them, and visualize the result in a third graph.
Customizable Interpolation: Options for window size, signal gap (positive for separation, negative for overlap), and interpolator choice.
Export and Report
Snapshot & Report Generation: Capture snapshots of graphs for reporting purposes, including statistical data on glued signals.

