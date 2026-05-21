# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip

from typing import Optional

from guidata.qthelpers import get_std_icon  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.gui.states.signals import TMSignals
from moduletester.model import Test


class _CommentTextEdit(QW.QTextEdit):
    """Custom QTextEdit can emit a specific signal when the user presses Ctrl+Z and all
    available undo operations have been exhausted.

    Args:
        parent: Parent widget. Defaults to None.
    """

    sig_reset_comment = QC.Signal()  # type: ignore

    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.allow_reset_content = False
        self.undoAvailable.connect(self.set_allow_reset_content)

    def set_allow_reset_content(self, avail: bool):
        """Set whether the content can be reset."""
        self.allow_reset_content = not avail

    def keyPressEvent(self, e: QG.QKeyEvent) -> None:  # noqa: N802
        """Handle key press events.

        Args:
            e: Key event.
        """
        super().keyPressEvent(e)
        if (
            self.allow_reset_content
            and e.key() == QC.Qt.Key.Key_Z
            and e.modifiers() == QC.Qt.ControlModifier
        ):
            self.sig_reset_comment.emit()
            self.allow_reset_content = False


class TestCommentWidget(QW.QWidget):
    """Widget to display and edit the comment of a test result.

    Args:
        signals: Signals object that contains shared global ModuleTester signals.
        parent: Parent widget. Defaults to None.
    """

    SIG_EDIT_STOPPED = QC.Signal()  # type: ignore

    def __init__(self, signals: TMSignals, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)

        self.cached_comments: dict[str, str] = {}

        self.signals = signals

        # Widgets
        self.lbl_icon = QW.QLabel()
        self.lbl_icon.setFixedWidth(32)

        self.comment_label = _CommentTextEdit()
        self.comment_label.setWordWrapMode(QG.QTextOption.WordWrap)
        self.comment_label.setFrameStyle(0)

        for label in (self.comment_label, self.lbl_icon):
            label.setAlignment(QC.Qt.AlignmentFlag.AlignTop)

        # Event Handlers
        self.comment_label.textChanged.connect(self.text_changed)  # type: ignore
        self.comment_label.sig_reset_comment.connect(self.reset_comment)

        self.timer = QC.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(1000)

        self.timer.timeout.connect(self.SIG_EDIT_STOPPED)
        self.comment_label.textChanged.connect(self.text_changed)
        self.SIG_EDIT_STOPPED.connect(self.update_cached_comment)

        # Layouts
        self.hlayout = QW.QHBoxLayout(self)
        self.hlayout.addWidget(self.lbl_icon)
        self.hlayout.addWidget(self.comment_label)

        self.test: Optional[Test] = None

    def reset_comment(self):
        """Reset the comment to the last saved version."""
        text = "No result yet"
        if self.test is not None and self.test.result is not None:
            text = self.test.result.comment
            self.cached_comments.pop(self.test.package.full_name, None)
        self.comment_label.setText(text)

    def readonly(self, readonly: bool):
        """Set the comment label to readonly or not.

        Args:
            readonly: Whether the comment label should be readonly.
        """
        if readonly:
            self.comment_label.setTextInteractionFlags(
                QC.Qt.TextInteractionFlag.TextSelectableByMouse
            )
        else:
            self.comment_label.setTextInteractionFlags(
                QC.Qt.TextInteractionFlag.TextEditorInteraction
            )

    def set_item(self, test: Test):
        """Set the test item to display the comment of."""
        # save previous changes if save timer was still running
        if self.timer.isActive():
            self.timer.stop()
            self.update_cached_comment()

        self.test = test
        cached_comment = self.cached_comments.get(test.package.full_name, None)
        if test.result is not None:
            text = test.result.comment if cached_comment is None else cached_comment
            self.readonly(False)
        elif test.is_running():
            text = "No result yet"
            self.readonly(False)
        else:
            text = "No result yet"
            self.readonly(True)

        self.lbl_icon.setPixmap(get_std_icon("MessageBoxInformation").pixmap(24, 24))
        self.comment_label.blockSignals(True)
        self.comment_label.setText(text)
        self.comment_label.blockSignals(False)
        self.comment_label.undoAvailable.emit(False)

    def text_changed(self) -> None:
        """Emit SIG_EDIT_STOPPED after a delay so some actions are not trigger at
        every key stroke."""
        """Text has changed: restart the timer to emit SIG_EDIT_STOPPED after a delay"""
        self.signals.SIG_PROJECT_MODIFIED.emit()
        if self.timer.isActive():
            self.timer.stop()
        self.timer.start()

    def update_cached_comment(self):
        """Update the cached comment with the current comment."""
        if self.test is None:
            return
        self.cached_comments[self.test.package.full_name] = (
            self.comment_label.toPlainText()
        )
