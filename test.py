import sys
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Create a custom Matplotlib widget by subclassing FigureCanvas
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        plt.tight_layout()

# Main window class that embeds the canvas and handles updating the plot
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ecg_signal):
        super(MainWindow, self).__init__()
        self.ecg_signal = ecg_signal

        # Define the window size (number of points) that you'll display at once.
        self.window_size = 500  # adjust based on your signal and preferences
        self.current_index = 0

        # Set up the Matplotlib canvas
        self.canvas = MplCanvas(self)
        self.setCentralWidget(self.canvas)
        self.canvas.ax.set_xlabel("Time (index)")
        self.canvas.ax.set_ylabel("Amplitude")
        self.canvas.ax.set_title("ECG Signal - Cine Mode")

        # Plot the initial window of the signal
        self.x_data = np.arange(self.window_size)
        self.y_data = self.ecg_signal[:self.window_size]
        self.line, = self.canvas.ax.plot(self.x_data, self.y_data, lw=2)

        # Set reasonable x and y axis limits
        self.canvas.ax.set_xlim(0, self.window_size)
        self.canvas.ax.set_ylim(np.min(self.y_data) - 0.1 * np.ptp(self.y_data),
                                np.max(self.y_data) + 0.1 * np.ptp(self.y_data))

        # Set up a QTimer to update the plot periodically
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(50)  # in milliseconds; adjust the speed as needed
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Advance the current index to slide the window along the signal
        step = 10  # slide by 10 points; adjust for a smoother or faster movement
        self.current_index += step

        # Loop back to the beginning if the end is reached
        if self.current_index + self.window_size >= len(self.ecg_signal):
            self.current_index = 0

        # Get the new segment of data
        new_y_data = self.ecg_signal[self.current_index : self.current_index + self.window_size]
        new_x_data = np.arange(self.current_index, self.current_index + self.window_size)

        # Update the data of the line object
        self.line.set_xdata(new_x_data)
        self.line.set_ydata(new_y_data)

        # Update x-axis limits to match new data window
        self.canvas.ax.set_xlim(new_x_data[0], new_x_data[-1])
        self.canvas.ax.set_ylim(np.min(new_y_data) - 0.1 * np.ptp(new_y_data),
                                np.max(new_y_data) + 0.1 * np.ptp(new_y_data))

        # Redraw the canvas
        self.canvas.draw()

if __name__ == '__main__':
    # Load the .mat file (adjust the file name/path as needed)
    mat_contents = sio.loadmat('A00004.mat')
    # 'val' is assumed to be the key for the ECG signal; it might need a squeeze.
    ecg_signal = mat_contents['val'].squeeze()

    # Initialize the Qt application and main window
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(ecg_signal)
    main_window.show()
    sys.exit(app.exec_())
