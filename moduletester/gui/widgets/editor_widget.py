from __future__ import annotations

from abc import ABC
from typing import Optional

from guidata.qthelpers import get_icon
from guidata.widgets import codeeditor
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.gui.widgets.dockable_widget import DockableQWidget


class DialogEditor(codeeditor.CodeEditor):
    sig_update_content = QC.Signal()  # type: ignore
    sig_save_key = QC.Signal()  # type: ignore

    def __init__(
        self,
        parent: Optional[QW.QWidget] = None,
        language=None,
        font=None,
        columns=None,
        rows=None,
    ):
        super().__init__(parent, language, font, columns, rows)  # type: ignore
        self.content_is_synched = True

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore # noqa: N802
        if not self.content_is_synched:
            self.sig_update_content.emit()
        super().closeEvent(event)

    def keyPressEvent(self, event: QG.QKeyEvent):  # type: ignore  # noqa: N802
        super().keyPressEvent(event)
        if (
            event.modifiers() == QC.Qt.ControlModifier
            and event.key() == QC.Qt.Key.Key_S
        ):
            self.sig_save_key.emit()
            self.content_is_synched = True
        else:
            self.content_is_synched = False


class Editor(DockableQWidget, ABC):
    """Editor widget with a read-only code editor and a button to open a popup editor.
    The editors are guidata.widgets.codeeditor.CodeEditor objects.

    Args:
        parent: Parent widget. Defaults to None.
        title: Widget title. Defaults to "Editor".
        language: Language to use for the code editor (see guidata documentation).
            Defaults to None.
        additional_btns: Additional buttons to add to the widget. Defaults to None.
    """

    sig_save_text = QC.Signal(str)  # type: ignore

    def __init__(
        self,
        parent: QWidget | None,
        title: str = "Editor",
        language: str | None = None,
        additional_btns: Optional[list[QW.QPushButton]] = None,
    ) -> None:
        super().__init__(parent, title)

        self._vlayout = QW.QVBoxLayout()
        self._hlayout = QW.QHBoxLayout()

        self.editor_edit_btn = QW.QPushButton(
            get_icon("libre-gui-action-edit.svg"), "Edit"
        )
        self.editor_save_btn = QW.QPushButton(get_icon("libre-gui-save.svg"), "Save")
        self.readonly_editor = codeeditor.CodeEditor(self, language=language, rows=True)
        self.readonly_editor.setReadOnly(True)
        self.popup_editor = DialogEditor(
            self,
            columns=100,
            rows=45,
            language=language,
        )
        self.popup_editor.sig_save_key.connect(self.update_content)
        self.popup_editor.sig_save_key.connect(self.save_text)
        self.additional_btns = additional_btns or []

        self.change_saved = True

        self.setup()

    def set_text(self, text: str) -> None:
        """Set the text of the readonly editor.

        Args:
            text: Text to set.
        """
        self.readonly_editor.setPlainText(text)

    def get_text(self) -> str:
        """Get the text of the readonly editor."""
        return self.readonly_editor.toPlainText()

    def update_content(self) -> None:
        """Update the content of the readonly editor with the content of the popup
        editor."""
        self.readonly_editor.setPlainText(self.popup_editor.toPlainText())
        self.change_saved = False
        self.editor_save_btn.setEnabled(True)

    def open_popup_editor(self):
        """Open the popup editor with the content of the readonly editor."""
        self.popup_editor.setPlainText(self.readonly_editor.toPlainText())
        self.popup_editor.show()

    def save_text(self) -> None:
        """Emit the sig_save_text signal with the content of the readonly editor."""
        self.sig_save_text.emit(self.readonly_editor.toPlainText())

    def saved(self) -> None:
        """Set the change_saved attribute to True and disable the save button."""
        self.change_saved = True
        self.editor_save_btn.setEnabled(False)

    def setup(self):
        """Setup the widget."""
        self.editor_save_btn.clicked.connect(self.save_text)
        self.editor_save_btn.setEnabled(False)
        self.editor_edit_btn.clicked.connect(self.open_popup_editor)

        self._vlayout.addWidget(self.readonly_editor)
        self._hlayout.addWidget(self.editor_edit_btn)
        self._hlayout.addWidget(self.editor_save_btn)
        self._vlayout.addLayout(self._hlayout)

        self.popup_editor.setWindowTitle("Edit...")
        self.popup_editor.setWindowIcon(get_icon("libre-gui-action-edit.svg"))
        self.popup_editor.setWindowFlags(QC.Qt.WindowType.Window)
        self.popup_editor.sig_update_content.connect(self.update_content)

        if len(self.additional_btns) > 0:
            splitter = QW.QSplitter()
            splitter.setStyleSheet("QSplitter::border {border: 1px solid #d3d3d3;}")
            self._vlayout.addWidget(splitter)

        for btn in self.additional_btns:
            self._vlayout.addWidget(btn)

        self.setLayout(self._vlayout)
