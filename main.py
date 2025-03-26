import sys
import numpy as np
import scipy.io as sio
from PyQt5 import QtWidgets, QtCore, uic, QtGui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui.ui", self)  # Load UI file

        # Find the QGraphicsView in the UI
        self.graphics_view = self.findChild(QtWidgets.QGraphicsView, "ECG_graphicsView")
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        # Load button
        self.load_button = self.findChild(QtWidgets.QPushButton, "load_btn")
        self.load_button.clicked.connect(self.load_signal)

        # Timer for updating the ECG signal
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot)

        self.ecg_signal = None
        self.window_size = 1500
        self.current_index = 0
        self.path_item = None  # Placeholder for ECG path

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

    def update_plot(self):
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
        self.path_item = self.scene.addPath(path, QtGui.QPen(QtGui.QColor("red"), 2))

        # Adjust the view
        self.graphics_view.setSceneRect(0, 0, self.window_size, 100)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
