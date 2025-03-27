import sys
import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.signal import butter, find_peaks, filtfilt
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from dummies import SPO2Graph, ABPGraph, RESPGraph 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui.ui", self)  

        # ECG Graph
        self.graphics_view = self.findChild(
            QtWidgets.QGraphicsView, "ECG_graphicsView")
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        # Dummy Graphs
        self.spo2_graph = SPO2Graph(self.findChild(
            QtWidgets.QGraphicsView, "SPO2_graficsView"))
        self.abp_graph = ABPGraph(self.findChild(
            QtWidgets.QGraphicsView, "ABP_graphicsView"))
        self.resp_graph = RESPGraph(self.findChild(
            QtWidgets.QGraphicsView, "RESP_graphiicsView"))

        # heart rate label
        self.hr_label = self.findChild(QtWidgets.QLabel, "HR_label")
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

        # alarm styles
        self.normal_siren_style = (
            "QWidget{\nbackground-color : rgb(38,38,59);\n	\n\n"
            "        border-radius: 10px;\n        padding: 10px;\n"
            "        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);\n\n}"
        )
        self.alarm_siren_style = (
            "QWidget{\nbackground-color : red;\n	\n\n"
            "        border-radius: 10px;\n        padding: 10px;\n"
            "        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);\n\n}"
        )

    def load_signal(self):
        """Loads an ECG signal from a .mat file and starts plotting."""

        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open ECG Signal", "", "MAT Files (*.mat);;CSV Files (*.csv)")

        if file_path:
            # reset alarms
            if hasattr(self, 'alarm_timer'):
                try:
                    self.alarm_timer.timeout.disconnect()
                except:
                    pass

                self.AF_widget.setStyleSheet(self.normal_siren_style)
                self.bradycardia_widget.setStyleSheet(self.normal_siren_style)
                self.VT_widget.setStyleSheet(self.normal_siren_style)

            try:
                if file_path.endswith('.mat'):
                    mat_contents = sio.loadmat(file_path)
                    self.ecg_signal = mat_contents['val'].squeeze()
                    self.fs = 360
                    self.detect_AF()

                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    time = df['Time'].to_numpy()
                    self.ecg_signal = df['Amplitude'].to_numpy()
                    self.fs = 1 / (time[1] - time[0])
                    self.detect_VT_OR_Bradycardia()
                else:
                    raise ValueError(
                        "Unsupported file format. Please use .mat or .csv files.")
                # Reset index and stop previous playback
                self.current_index = 0
                self.timer.stop()
                self.path_item = None
                self.scene.clear()
                # Start the animation
                self.timer.start()

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Failed to load ECG signal: {e}")

    def update_plots(self):
        """Updates all plots."""
        self.update_ecg_plot()
        self.spo2_graph.update_plot()
        self.abp_graph.update_plot()
        self.resp_graph.update_plot()

    def update_ecg_plot(self):
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

        if self.path_item is not None and self.path_item.scene() == self.scene:
            self.scene.removeItem(self.path_item)

        # Add new path to the scene
        self.path_item = self.scene.addPath(path, QtGui.QPen(QtGui.QColor(85, 255, 0), 2))

        # Adjust the view
        self.graphics_view.setSceneRect(0, 0, self.window_size, 100)

    def detect_AF(self):
        """Detects arrythmia in the ECG signal."""
        min_distance = int(0.4 * self.fs)
        peaks, _ = find_peaks(
            self.ecg_signal, distance=min_distance, prominence=1)

        rr_intervals = np.diff(peaks) / self.fs
        heart_rate = 60 / np.mean(rr_intervals)
        self.hr_label.setText(str(int(heart_rate)))

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
                self.alarm_siren(self.AF_widget)
                # activate alarm of AF

            else:
                print("Heart rhythm appears regular based on our RR interval analysis.")
                # no AF detected - normal rhythm
        else:
            print("Not enough beats detected for arrhythmia analysis.")

    def detect_VT_OR_Bradycardia(self):
        """Detects ventricular tachycardia or bradycardia in the ECG signal."""
        # self.fs = 300    # sampling frequency of the data

        min_distance = int(0.4 * self.fs)

        peaks, properties = find_peaks(
            self.ecg_signal, distance=min_distance, prominence=1)

        # Time differences between peaks
        rr_intervals = np.diff(peaks) / self.fs
        heart_rate = 60 / np.mean(rr_intervals)
        self.hr_label.setText(str(int(heart_rate)))

        if heart_rate > 100:
            condition = "Ventricular Tachycardia (heart rate > 100 BPM)"
            self.alarm_siren(self.VT_widget)
            print(condition)
            # activate alarm of VT
        elif heart_rate < 60:
            condition = "Bradycardia (heart rate < 60 BPM)"
            self.alarm_siren(self.bradycardia_widget)
            print(condition)
            # activate alarm of bradycardia
        else:
            condition = "Normal heart rate"
            print(condition)
            # no alarm - normal

    def alarm_siren(self, widget):
        """Continuously toggles the alarm style on the widget."""        
        self.alarm_timer = QtCore.QTimer(self)
        self.alarm_state = True  # Track the current state normal or alarm

        def toggle_style():
            if self.alarm_state:
                widget.setStyleSheet(self.alarm_siren_style)
            else:
                widget.setStyleSheet(self.normal_siren_style)
            self.alarm_state = not self.alarm_state 

        # Connect the timer to the toggle function
        self.alarm_timer.timeout.connect(toggle_style)
        self.alarm_timer.start(2000) 


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
