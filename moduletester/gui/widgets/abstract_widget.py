from abc import ABC, ABCMeta

import qtpy.QtWidgets as QW


class MetaAbstractQWidget(ABCMeta, type(QW.QWidget)):
    """Metaclass that combines ABCMeta and QWidget metaclasses."""


class AbstractQWidget(ABC, QW.QWidget, metaclass=MetaAbstractQWidget):
    """Abstract QWidget."""
