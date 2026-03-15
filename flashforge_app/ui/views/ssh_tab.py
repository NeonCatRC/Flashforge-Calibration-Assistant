from __future__ import annotations

from pathlib import Path
from typing import List

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import paramiko
from scp import SCPClient

from flashforge_app.services.localization import LocalizationService
from flashforge_app.state import AppState


class _SSHWorker(QObject):
    """Runs SSH operations off the main thread."""

    log = Signal(str)
    config_ready = Signal(Path)
    shapers_ready = Signal(list)
    finished = Signal()

    def __init__(self, host: str, username: str, password: str) -> None:
        super().__init__()
        self._host = host
        self._username = username
        self._password = password

    def _connect(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self._host, username=self._username, password=self._password, timeout=15)
        return client

    def run_test(self) -> None:
        try:
            client = self._connect()
            _stdin, stdout, stderr = client.exec_command('echo "test"')
            exit_status = stdout.channel.recv_exit_status()
            client.close()
            if exit_status == 0:
                self.log.emit("__OK__")
            else:
                self.log.emit("__ERR__" + stderr.read().decode().strip())
        except Exception as exc:
            self.log.emit("__ERR__" + str(exc))
        finally:
            self.finished.emit()

    def run_fetch_config(self, remote_paths: list[str]) -> None:
        try:
            client = self._connect()
            with SCPClient(client.get_transport()) as scp:
                local_path = Path("config/printer.cfg")
                local_path.parent.mkdir(parents=True, exist_ok=True)
                last_error = None
                for remote_path in remote_paths:
                    try:
                        scp.get(remote_path, str(local_path))
                        self.log.emit("__CFG__" + str(local_path))
                        self.config_ready.emit(local_path)
                        break
                    except Exception as exc:
                        last_error = exc
                else:
                    raise last_error or FileNotFoundError("printer.cfg not found on remote host")
            client.close()
        except Exception as exc:
            self.log.emit("__ERR__" + str(exc))
        finally:
            self.finished.emit()

    def run_fetch_shapers(self) -> None:
        try:
            client = self._connect()
            _stdin, stdout, stderr = client.exec_command("ls /tmp/calibration_data_*.csv")
            files = [line.strip() for line in stdout.read().decode().splitlines() if line.strip()]
            err = stderr.read().decode().strip()
            if err:
                self.log.emit(err)
            if not files:
                self.log.emit("__NO_SHAPERS__")
                client.close()
                self.finished.emit()
                return

            local_dir = Path("config/shapers")
            local_dir.mkdir(parents=True, exist_ok=True)
            downloaded: List[Path] = []
            with SCPClient(client.get_transport()) as scp:
                for remote_file in files:
                    local_file = local_dir / Path(remote_file).name
                    scp.get(remote_file, str(local_file))
                    downloaded.append(local_file)
            client.close()

            for entry in downloaded:
                self.log.emit("__SHAPER__" + str(entry))
            self.shapers_ready.emit(downloaded)
        except Exception as exc:
            self.log.emit("__ERR__" + str(exc))
        finally:
            self.finished.emit()


class SSHTab(QWidget):
    """Dedicated SSH tab for testing connection and downloading files."""

    config_downloaded = Signal(Path)
    shaper_files_downloaded = Signal(list)

    def __init__(
        self,
        localization: LocalizationService,
        app_state: AppState,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.localization = localization
        self.app_state = app_state
        self._current_settings = self.app_state.current_settings.ssh

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.header_label = QLabel(self.localization.translate("settings_tab.ssh"))
        self.header_label.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(self.header_label)

        credentials_frame = QFrame()
        credentials_frame.setObjectName("Card")
        form_layout = QFormLayout()
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(12)
        credentials_frame.setLayout(form_layout)

        self.host_input = QLineEdit(self._current_settings.host)
        self.user_input = QLineEdit(self._current_settings.username)
        self.password_input = QLineEdit(self._current_settings.password)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.path_input = QLineEdit(self._current_settings.printer_cfg_path or "")

        form_layout.addRow(self.localization.translate("settings_tab.host"), self.host_input)
        form_layout.addRow(self.localization.translate("settings_tab.username"), self.user_input)
        form_layout.addRow(self.localization.translate("settings_tab.password"), self.password_input)
        form_layout.addRow(self.localization.translate("settings_tab.printer_cfg_path"), self.path_input)

        layout.addWidget(credentials_frame)

        buttons_frame = QFrame()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)
        buttons_frame.setLayout(btn_layout)

        self.test_button = QPushButton(self.localization.translate("settings_tab.test_connection"))
        self.test_button.clicked.connect(self._on_test_connection)
        btn_layout.addWidget(self.test_button)

        self.fetch_config_button = QPushButton(self.localization.translate("settings_tab.get_printer_cfg"))
        self.fetch_config_button.clicked.connect(self._on_fetch_config)
        btn_layout.addWidget(self.fetch_config_button)

        self.fetch_shapers_button = QPushButton(self.localization.translate("settings_tab.get_shapers"))
        self.fetch_shapers_button.clicked.connect(self._on_fetch_shapers)
        btn_layout.addWidget(self.fetch_shapers_button)

        btn_layout.addStretch(1)
        layout.addWidget(buttons_frame)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setObjectName("Subtitle")
        self.log_output.setStyleSheet("background: transparent; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;")
        layout.addWidget(self.log_output)

        self._worker_thread: QThread | None = None
        self._worker: _SSHWorker | None = None
        self._action_buttons = [self.test_button, self.fetch_config_button, self.fetch_shapers_button]

    def apply_translations(self) -> None:
        tr = self.localization.translate
        self.header_label.setText(tr("settings_tab.ssh"))
        self.test_button.setText(tr("settings_tab.test_connection"))
        self.fetch_config_button.setText(tr("settings_tab.get_printer_cfg"))
        self.fetch_shapers_button.setText(tr("settings_tab.get_shapers"))

    # ------------------------------------------------------------------ helpers
    def _append_log(self, message: str) -> None:
        if message:
            self.log_output.append(message)
        self.log_output.moveCursor(QTextCursor.End)

    # ------------------------------------------------------------------ worker helpers
    def _validate_inputs(self) -> bool:
        host = self.host_input.text().strip()
        username = self.user_input.text().strip()
        password = self.password_input.text()
        if not host or not username or not password:
            self._append_log(self.localization.translate("settings_tab.fill_ssh"))
            return False
        return True

    def _start_worker(self, job_method_name: str, *args) -> None:
        if self._worker_thread and self._worker_thread.isRunning():
            return
        if not self._validate_inputs():
            return

        self.save_credentials()
        for btn in self._action_buttons:
            btn.setEnabled(False)

        self._worker_thread = QThread()
        self._worker = _SSHWorker(
            self.host_input.text().strip(),
            self.user_input.text().strip(),
            self.password_input.text(),
        )
        self._worker.moveToThread(self._worker_thread)
        self._worker.log.connect(self._handle_worker_log)
        self._worker.config_ready.connect(self._handle_config_ready)
        self._worker.shapers_ready.connect(self._handle_shapers_ready)
        self._worker.finished.connect(self._on_worker_finished)

        method = getattr(self._worker, job_method_name)
        self._worker_thread.started.connect(lambda: method(*args))
        self._worker_thread.start()

    def _on_worker_finished(self) -> None:
        for btn in self._action_buttons:
            btn.setEnabled(True)
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait()
            self._worker_thread = None
        self._worker = None

    def _handle_worker_log(self, msg: str) -> None:
        tr = self.localization.translate
        if msg == "__OK__":
            self._append_log(tr("settings_tab.connection_success"))
        elif msg == "__NO_SHAPERS__":
            self._append_log(tr("settings_tab.no_shapers_found"))
        elif msg.startswith("__ERR__"):
            self._append_log(tr("settings_tab.connection_error").format(msg[7:]))
        elif msg.startswith("__CFG__"):
            self._append_log(tr("settings_tab.fill_printer_cfg").format(msg[7:]))
        elif msg.startswith("__SHAPER__"):
            self._append_log(tr("settings_tab.fill_shapers").format(msg[10:]))
        else:
            self._append_log(msg)

    def _handle_config_ready(self, local_path: Path) -> None:
        self.app_state.load_printer_config(local_path)
        self.config_downloaded.emit(local_path)

    def _handle_shapers_ready(self, files: list[Path]) -> None:
        self.shaper_files_downloaded.emit(files)

    # ------------------------------------------------------------------ slots
    def _on_test_connection(self) -> None:
        self._start_worker("run_test")

    def _on_fetch_config(self) -> None:
        self._start_worker("run_fetch_config", self._build_remote_paths())

    def _on_fetch_shapers(self) -> None:
        self._start_worker("run_fetch_shapers")

    # ------------------------------------------------------------------ persistence
    def _build_remote_paths(self) -> list[str]:
        custom = self.path_input.text().strip()
        defaults = [
            "/opt/config/printer.cfg",
            "/root/printer_data/config/printer.cfg",
            "/usr/data/config/printer.cfg",
        ]
        ordered = []
        if custom:
            ordered.append(custom)
        ordered.extend(defaults)
        seen: list[str] = []
        for path in ordered:
            if path and path not in seen:
                seen.append(path)
        return seen

    def save_credentials(self) -> None:
        ssh_settings = self.app_state.current_settings.ssh
        ssh_settings.host = self.host_input.text().strip()
        ssh_settings.username = self.user_input.text().strip()
        ssh_settings.password = self.password_input.text()
        ssh_settings.printer_cfg_path = self.path_input.text().strip()
        self.app_state.save_settings()
