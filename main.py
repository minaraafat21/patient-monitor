import sys
import numpy as np
import scipy.io as sio
from scipy.signal import butter, find_peaks, filtfilt
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from dummies import SPO2Graph, ABPGraph, RESPGraph  # Import the other graphs

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui.ui", self)  # Load UI file

        # ECG Graph
        self.graphics_view = self.findChild(QtWidgets.QGraphicsView, "ECG_graphicsView")
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        # Other Graphs
        self.spo2_graph = SPO2Graph(self.findChild(QtWidgets.QGraphicsView, "SPO2_graficsView"))
        self.abp_graph = ABPGraph(self.findChild(QtWidgets.QGraphicsView, "ABP_graphicsView"))
        self.resp_graph = RESPGraph(self.findChild(QtWidgets.QGraphicsView, "RESP_graphiicsView"))

        # Load button
        self.load_button = self.findChild(QtWidgets.QPushButton, "load_btn")
        self.load_button.clicked.connect(self.load_signal)

        # Timer for updating the plots
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plots)

        self.ecg_signal = None
        self.window_size = 1500
        self.current_index = 0
        self.path_item = None  # Placeholder for ECG path
        self.fs = None

    def load_signal(self):
        """Loads an ECG signal from a .mat file and starts plotting."""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open ECG Signal", "", "MAT Files (*.mat)")

        if file_path:
            try:
                mat_contents = sio.loadmat(file_path)
                self.ecg_signal = mat_contents['val'].squeeze()

                # Reset index and stop previous playback
                self.current_index = 0
                self.timer.stop()

                # Clear previous plots
                self.scene.clear()

                # Start the animation
                self.timer.start()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load ECG signal: {e}")

    def update_plots(self):
        """Updates all plots."""
        self.update_ecg_plot()
        self.spo2_graph.update_plot()
        self.abp_graph.update_plot()
        self.resp_graph.update_plot()

    def update_ecg_plot(self):
        """Updates the ECG signal in the QGraphicsView."""
        if self.ecg_signal is None:
            return

        self.current_index += 5
        if self.current_index + self.window_size >= len(self.ecg_signal):
            self.current_index = 0  # Restart when reaching the end

        # Prepare the ECG segment to be drawn
        x_data = np.arange(self.window_size)
        y_data = self.ecg_signal[self.current_index:self.current_index + self.window_size]

        # Normalize for display
        y_data = (y_data - np.min(y_data)) / (np.max(y_data) - np.min(y_data)) * 100
        y_data = 100 - y_data  # Flip for correct orientation

        # Create a new ECG path
        path = QtGui.QPainterPath()
        path.moveTo(x_data[0], y_data[0])
        for x, y in zip(x_data, y_data):
            path.lineTo(x, y)

        # Remove old path and add new one
        if self.path_item:
            self.scene.removeItem(self.path_item)
        self.path_item = self.scene.addPath(path, QtGui.QPen(QtGui.QColor(85,255,0), 2))

        # Adjust the view
        self.graphics_view.setSceneRect(0, 0, self.window_size, 100)

    def detect_AF(self):
        """Detects arrythmia in the ECG signal."""
        self.fs = 360

        min_distance = int(0.4 * self.fs)
        peaks, properties = find_peaks(self.ecg_signal, distance=min_distance, prominence=1)

        rr_intervals = np.diff(peaks) / self.fs

        if len(rr_intervals) > 1:
            mean_rr = np.mean(rr_intervals)
            std_rr = np.std(rr_intervals)
            coeff_variation = std_rr / mean_rr  # relative variability

            print("Mean RR Interval: {:.3f} s".format(mean_rr))
            print("STD of RR Intervals: {:.3f} s".format(std_rr))
            print("Coefficient of Variation: {:.3f}".format(coeff_variation))
            
            variability_threshold = 0.1 
            if coeff_variation > variability_threshold:
                print("Atrial fibrillation detected: High variability in RR intervals!")
                # activate alarm of AF

            else:
                print("Heart rhythm appears regular based on our RR interval analysis.")
                # No AF detected - normal rhythm
        else:
            print("Not enough beats detected for arrhythmia analysis.")
    
    def detect_VT_OR_Bradycardia(self):
        """Detects ventricular tachycardia or bradycardia in the ECG signal."""
        # self.fs = 300    # sampling frequency of the data

        min_distance = int(0.4 * self.fs)

        peaks, properties = find_peaks(self.ecg_signal, distance=min_distance, prominance=1)  # Adjust 'height' and 'distance' based on your data

        rr_intervals = np.diff(peaks) / self.fs # Time differences between peaks
        heart_rate = 60 / np.mean(rr_intervals)

        if heart_rate > 100:
            condition = "Ventricular Tachycardia (heart rate > 100 BPM)"
            # activate alarm of VT
        elif heart_rate < 60:
            condition = "Bradycardia (heart rate < 60 BPM)"
            # activate alarm of bradycardia
        else:
            condition = "Normal heart rate"
            # no alarm - normal

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
