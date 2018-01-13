import locale
import time

from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QCloseEvent, QIcon, QTransform
from PyQt5.QtWidgets import QDialog, QGraphicsView

from urh import constants
from urh.controller.widgets.DeviceSettingsWidgetController import DeviceSettingsWidgetController
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.ui.ui_send_recv import Ui_SendRecvDialog
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class SendRecvDialogController(QDialog):
    recording_parameters = pyqtSignal(str, dict)

    def __init__(self, project_manager: ProjectManager, is_tx: bool, parent=None, testing_mode=False):
        super().__init__(parent)
        self.is_tx = is_tx
        self.update_interval = 25

        self.setWindowFlags(Qt.Window)
        self.testing_mode = testing_mode

        self.ui = Ui_SendRecvDialog()
        self.ui.setupUi(self)
        self.ui.splitter.setHandleWidth(6)

        self.set_sniff_ui_items_visible(False)

        self.graphics_view = None  # type: QGraphicsView

        self.backend_handler = BackendHandler()

        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(False)
        self.ui.btnSave.setEnabled(False)

        self.start = 0

        self.device_settings_widget = DeviceSettingsWidgetController(project_manager, is_tx)
        self.ui.scrollAreaWidgetContents_2.layout().insertWidget(0, self.device_settings_widget)

        if testing_mode:
            self.device_settings_widget.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        self.timer = QTimer(self)

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

        self.ui.splitter.setSizes([0.4 * self.width(), 0.6 * self.width()])

    @property
    def is_rx(self) -> bool:
        return not self.is_tx

    @property
    def has_empty_device_list(self):
        return self.device_settings_widget.ui.cbDevice.count() == 0

    @property
    def device(self) -> VirtualDevice:
        return self.device_settings_widget.device

    @device.setter
    def device(self, value):
        self.device_settings_widget.device = value

    @property
    def selected_device_name(self) -> str:
        return self.device_settings_widget.ui.cbDevice.currentText()

    def _eliminate_graphic_view(self):
        if self.graphics_view is not None:
            self.graphics_view.eliminate()

        self.graphics_view = None

    def hide_send_ui_items(self):
        for item in ("lblCurrentRepeatValue", "progressBarMessage",
                     "lblRepeatText", "lSamplesSentText", "progressBarSample", "labelCurrentMessage"):
            getattr(self.ui, item).hide()

    def hide_receive_ui_items(self):
        for item in ("lSamplesCaptured", "lSamplesCapturedText", "lSignalSize", "lSignalSizeText",
                     "lTime", "lTimeText", "btnSave", "labelReceiveBufferFull", "lReceiveBufferFullText"):
            getattr(self.ui, item).hide()

    def set_sniff_ui_items_visible(self, visible: bool):
        self.ui.groupBoxSniffSettings.setVisible(visible)

    def set_device_ui_items_enabled(self, enabled: bool):
        self.device_settings_widget.setEnabled(enabled)

    def create_connects(self):
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        self.ui.btnStop.clicked.connect(self.on_stop_clicked)
        self.ui.btnClear.clicked.connect(self.on_clear_clicked)

        self.timer.timeout.connect(self.update_view)
        self.ui.sliderYscale.valueChanged.connect(self.on_slider_y_scale_value_changed)

        self.device_settings_widget.selected_device_changed.connect(self.on_selected_device_changed)

    def _create_device_connects(self):
        self.device.stopped.connect(self.on_device_stopped)
        self.device.started.connect(self.on_device_started)
        self.device.sender_needs_restart.connect(self._restart_device_thread)

    def reset(self):
        self.device.current_index = 0
        self.device.current_iteration = 0
        self.ui.lSamplesCaptured.setText("0")
        self.ui.lSignalSize.setText("0")
        self.ui.lTime.setText("0")
        self.ui.lblCurrentRepeatValue.setText("-")
        self.ui.progressBarSample.setValue(0)
        self.ui.progressBarMessage.setValue(0)
        self.ui.btnClear.setEnabled(False)
        self.ui.btnSave.setEnabled(False)

    def init_device(self):
        pass

    def save_before_close(self):
        return True

    @pyqtSlot()
    def on_selected_device_changed(self):
        self.scene_manager.plot_data = None

        self.init_device()

        self.graphics_view.scene_manager = self.scene_manager
        self.graphics_view.setScene(self.scene_manager.scene)

    @pyqtSlot()
    def on_start_clicked(self):
        pass

    @pyqtSlot()
    def on_stop_clicked(self):
        self.device.stop("Stopped receiving: Stop button clicked")

    @pyqtSlot()
    def on_device_stopped(self):
        if self.graphics_view is not None:
            self.graphics_view.capturing_data = False
        self.set_device_ui_items_enabled(True)
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(True)
        self.ui.btnSave.setEnabled(self.device.current_index > 0)
        self.device_settings_widget.set_bandwidth_status()

        self.timer.stop()
        self.update_view()

    @pyqtSlot()
    def on_device_started(self):
        self.ui.txtEditErrors.clear()
        if self.graphics_view is not None:
            self.graphics_view.capturing_data = True
        self.ui.btnSave.setEnabled(False)
        self.ui.btnStart.setEnabled(False)

        self.ui.btnClear.setEnabled(False)
        self.device_settings_widget.ui.spinBoxNRepeat.setEnabled(False)
        self.ui.btnStop.setEnabled(True)

        self.timer.start(self.update_interval)

    def update_view(self):
        try:
            self.ui.sliderYscale.setValue(int(self.graphics_view.transform().m22()))
        except AttributeError:
            return

        txt = self.ui.txtEditErrors.toPlainText()
        new_messages = self.device.read_messages()

        if "No devices found for" in new_messages:
            self.device.stop_on_error("Could not establish connection to USRP")
            Errors.usrp_found()

            self.on_clear_clicked()

        elif any(e in new_messages for e in ("HACKRF_ERROR_NOT_FOUND", "HACKRF_ERROR_LIBUSB")):
            self.device.stop_on_error("Could not establish connection to HackRF")
            Errors.hackrf_not_found()
            self.on_clear_clicked()

        elif "No module named gnuradio" in new_messages:
            self.device.stop_on_error("Did not find gnuradio.")
            Errors.gnuradio_not_installed()
            self.on_clear_clicked()

        elif "RTLSDR-open: Error Code: -1" in new_messages:
            self.device.stop_on_error("Could not open a RTL-SDR device.")
            self.on_clear_clicked()

        elif "Address already in use" in new_messages:
            self._restart_device_thread()

        if len(new_messages) > 1:
            self.ui.txtEditErrors.setPlainText(txt + new_messages)

        self.ui.lSamplesCaptured.setText("{0:n}".format(self.device.current_index))
        self.ui.lSignalSize.setText(locale.format_string("%.2f", (8 * self.device.current_index) / (1024 ** 2)))
        self.ui.lTime.setText(locale.format_string("%.2f", self.device.current_index / self.device.sample_rate))

        if self.is_rx and self.device.data is not None and len(self.device.data) > 0:
            self.ui.labelReceiveBufferFull.setText("{0}%".format(int(100 * self.device.current_index /
                                                                     len(self.device.data))))

        if self.device.current_index == 0:
            return False

        return True

    def _restart_device_thread(self):
        self.device.stop("Restarting with new port")

        if self.device.backend == Backends.grc:
            self.device.increase_gr_port()

        self.device.start()

    @pyqtSlot()
    def on_clear_clicked(self):
        pass

    def closeEvent(self, event: QCloseEvent):
        self.timer.stop()

        self.device.stop("Dialog closed. Killing recording process.")
        logger.debug("Device stopped successfully.")

        if not self.testing_mode:
            if not self.save_before_close():
                event.ignore()
                return

        time.sleep(0.1)
        if self.device.backend not in (Backends.none, Backends.network):
            # Backend none is selected, when no device is available
            logger.debug("Cleaning up device")
            try:
                # For Protocol Sniffer
                self.device.index_changed.disconnect()
            except TypeError:
                pass

            self.device.cleanup()
            logger.debug("Successfully cleaned up device")
            self.recording_parameters.emit(str(self.device.name), dict(frequency=self.device.frequency,
                                                                       sample_rate=self.device.sample_rate,
                                                                       bandwidth=self.device.bandwidth,
                                                                       gain=self.device.gain,
                                                                       if_gain=self.device.if_gain,
                                                                       baseband_gain=self.device.baseband_gain,
                                                                       freq_correction=self.device.freq_correction
                                                                       ))

        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())

        if self.device is not None:
            self.device.free_data()

        self.scene_manager.eliminate()

        self._eliminate_graphic_view()

        super().closeEvent(event)

    @pyqtSlot(int)
    def on_slider_y_scale_value_changed(self, new_value: int):
        # Scale Up = Top Half, Scale Down = Lower Half
        transform = self.graphics_view.transform()
        self.graphics_view.setTransform(QTransform(transform.m11(), transform.m12(), transform.m13(),
                                                   transform.m21(), new_value, transform.m23(),
                                                   transform.m31(), transform.m32(), transform.m33()))
