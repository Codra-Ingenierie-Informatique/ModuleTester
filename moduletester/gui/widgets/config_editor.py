"""Configuration editor widget."""

from __future__ import annotations

import os

from PyQt5.QtWidgets import QWidget
from qtpy import QtWidgets as QW

import moduletester.config as cfg
from moduletester.gui.states.signals import TMSignals
from moduletester.gui.widgets.editor_widget import Editor


class ConfigEditor(Editor):
    """Widget for editing ModuleTester configuration files."""

    def __init__(
        self,
        parent: QWidget | None,
        signals: TMSignals,
        title: str = "Configuration Editor",
    ) -> None:
        """Editor for the configuration file.

        Args:
            parent: Parent widget. Defaults to None.
            signals: Signals object that contains shared global ModuleTester signals.
            title: Widget title. Defaults to "Configuration Editor".
        """
        self.signals = signals
        super().__init__(parent, title, language="yaml")

    def setup(self):
        """Setup the widget."""
        super().setup()
        self.read_config()
        self.sig_save_text.connect(self.save_config)
        self.signals.SIG_PROJECT_LOADED.connect(self.read_config)
        self.config_path = os.path.join(
            cfg.MODULETESTER_CONFIG_DIR, cfg.MODULETESTER_CONFIG_NAME
        )

    def save_config(self) -> None:
        """Tries to save the configuration file. This methods can handle errors and
        conflicts in the configuration file. by prompting with dialog boxes."""
        do_save = True
        if os.path.exists(self.config_path):
            do_save = (
                QW.QMessageBox.question(
                    self,
                    "Overwrite configuration file?",
                    f"Do you want to overwrite the existing file?\n{self.config_path}",
                    QW.QMessageBox.Yes | QW.QMessageBox.No,
                )
                == QW.QMessageBox.Yes
            )
        if do_save:
            config_content = self.get_text()
            try:
                cfg.load_conf_from_string(config_content)
            except cfg.ConfigConflictError as e:
                result = (
                    QW.QMessageBox.critical(
                        self,
                        "Error in configuration file",
                        f"Error in configuration file: {self.config_path}\n{str(e)}"
                        "\nDo you want to fix the error and save the file?",
                        QW.QMessageBox.Apply | QW.QMessageBox.Cancel,
                    )
                    == QW.QMessageBox.Apply
                )
                if not result:
                    return
                cfg.load_conf_from_string(config_content, resolve=True)
                self.set_text(cfg.conf_obj_to_str(cfg.PACKAGE_CONF))

            except cfg.InvalidPathError as e:
                QW.QMessageBox.critical(
                    self,
                    "Configuration file contains invalid values",
                    f"Configuration file {self.config_path} contains "
                    f"invalid value:\n {e.key} = {e.value}",
                    QW.QMessageBox.Cancel,
                )

            except Exception as e:
                QW.QMessageBox.critical(
                    self,
                    "Configuration file is invalid",
                    f"While Parsing the new configuration file, an error "
                    f"occurred:\n{str(e)}\n\n"
                    "The file will not be saved.",
                    QW.QMessageBox.Cancel,
                )
            cfg.save_config(cfg.PACKAGE_CONF, self.config_path)
            self.saved()

    def read_config(self) -> None:
        """Read the configuration file and display it in the editor. Can save the file
        if it does not exist."""
        cfg_exists = False
        config_content = cfg.conf_obj_to_str(cfg.PACKAGE_CONF)
        self.config_path = os.path.join(
            cfg.MODULETESTER_CONFIG_DIR, cfg.MODULETESTER_CONFIG_NAME
        )
        cfg_exists = os.path.exists(self.config_path)
        save_new_cfg = False
        if not cfg_exists:
            save_new_cfg = (
                QW.QMessageBox.question(
                    self,
                    "File not found",
                    f"Config file not found at {self.config_path}.\n"
                    "Do you want to create a new config file?",
                    QW.QMessageBox.Yes | QW.QMessageBox.No,
                )
                == QW.QMessageBox.Yes
            )

        if save_new_cfg and not cfg_exists:
            self.save_config()

        self.set_text(config_content)
        self.change_saved = True
        self.editor_save_btn.setEnabled(False)
