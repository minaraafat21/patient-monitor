from PyQt5 import QtWidgets, QtGui
import numpy as np

class SPO2Graph:
    def __init__(self, graphics_view):
        self.scene = QtWidgets.QGraphicsScene()
        graphics_view.setScene(self.scene)
        self.path_item = None
        self.window_size = 1500
        self.current_index = 0
        # Simpler SpO2 data: a sine wave with small random variations
        base_signal = 98 + np.sin(np.linspace(0, 20, 10000)) * 2
        noise = np.random.normal(0, 0.5, 10000)  # Small random noise
        self.spo2_signal = base_signal + noise

    def update_plot(self):
        """Update the SpO2 plot."""
        self.current_index += 5
        if self.current_index + self.window_size >= len(self.spo2_signal):
            self.current_index = 0  # Restart when reaching the end

        # Prepare the SpO2 segment to be drawn
        x_data = np.arange(self.window_size)
        y_data = self.spo2_signal[self.current_index:self.current_index + self.window_size]

        # Normalize for display
        y_data = (y_data - np.min(y_data)) / (np.max(y_data) - np.min(y_data)) * 100
        y_data = 100 - y_data  # Flip for correct orientation

        # Create a new SpO2 path
        path = QtGui.QPainterPath()
        path.moveTo(x_data[0], y_data[0])
        for x, y in zip(x_data, y_data):
            path.lineTo(x, y)

        # Remove old path and add new one
        if self.path_item:
            self.scene.removeItem(self.path_item)
        self.path_item = self.scene.addPath(path, QtGui.QPen(QtGui.QColor(0, 255, 255), 2))  # Cyan pen

class ABPGraph:
    def __init__(self, graphics_view):
        self.scene = QtWidgets.QGraphicsScene()
        graphics_view.setScene(self.scene)
        self.path_item = None
        self.window_size = 1500
        self.current_index = 0
        # Simpler ABP data: a sine wave with small random variations
        base_signal = 100 + np.sin(np.linspace(0, 30, 10000)) * 10
        noise = np.random.normal(0, 1, 10000)  # Small random noise
        self.abp_signal = base_signal + noise

    def update_plot(self):
        """Update the ABP plot."""
        self.current_index += 5
        if self.current_index + self.window_size >= len(self.abp_signal):
            self.current_index = 0  # Restart when reaching the end

        # Prepare the ABP segment to be drawn
        x_data = np.arange(self.window_size)
        y_data = self.abp_signal[self.current_index:self.current_index + self.window_size]

        # Normalize for display
        y_data = (y_data - np.min(y_data)) / (np.max(y_data) - np.min(y_data)) * 100
        y_data = 100 - y_data  # Flip for correct orientation

        # Create a new ABP path
        path = QtGui.QPainterPath()
        path.moveTo(x_data[0], y_data[0])
        for x, y in zip(x_data, y_data):
            path.lineTo(x, y)

        # Remove old path and add new one
        if self.path_item:
            self.scene.removeItem(self.path_item)
        self.path_item = self.scene.addPath(path, QtGui.QPen(QtGui.QColor(255, 0, 0), 2))  # Red pen

class RESPGraph:
    def __init__(self, graphics_view):
        self.scene = QtWidgets.QGraphicsScene()
        graphics_view.setScene(self.scene)
        self.path_item = None
        self.window_size = 1500
        self.current_index = 0
        # Simpler RESP data: a sine wave with small random variations
        base_signal = 50 + np.sin(np.linspace(0, 10, 10000)) * 20
        noise = np.random.normal(0, 2, 10000)  # Small random noise
        self.resp_signal = base_signal + noise

    def update_plot(self):
        """Update the RESP plot."""
        self.current_index += 5
        if self.current_index + self.window_size >= len(self.resp_signal):
            self.current_index = 0  # Restart when reaching the end

        # Prepare the RESP segment to be drawn
        x_data = np.arange(self.window_size)
        y_data = self.resp_signal[self.current_index:self.current_index + self.window_size]

        # Normalize for display
        y_data = (y_data - np.min(y_data)) / (np.max(y_data) - np.min(y_data)) * 100
        y_data = 100 - y_data  # Flip for correct orientation

        # Create a new RESP path
        path = QtGui.QPainterPath()
        path.moveTo(x_data[0], y_data[0])
        for x, y in zip(x_data, y_data):
            path.lineTo(x, y)

        # Remove old path and add new one
        if self.path_item:
            self.scene.removeItem(self.path_item)
        self.path_item = self.scene.addPath(path, QtGui.QPen(QtGui.QColor(255, 255, 0), 2))  # Yellow pen
