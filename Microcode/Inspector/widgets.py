"""
Helper widgets for the Microcode Inspector Tool
"""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QWidget,
)


# ============================================================
# LED Widget
# ============================================================

class LedWidget(QFrame):
    """Visual LED indicator for signal status"""

    def __init__(self):
        super().__init__()

        self.setFixedSize(14, 14)
        self.setStyleSheet("""
            border-radius: 7px;
            background-color: #ff2020;
        """)

    def SetState(self, state: bool):
        """Update LED color based on state (green = on, red = off)"""

        color = "#35ff5a" if state else "#ff2020"

        self.setStyleSheet(f"""
            border-radius: 7px;
            background-color: {color};
        """)


# ============================================================
# Signal Widget
# ============================================================

class SignalWidget(QWidget):
    """Signal display with LED indicator and label"""

    def __init__(self, signalName):
        super().__init__()

        self.led = LedWidget()

        self.label = QLabel(signalName)
        self.label.setStyleSheet("""
            color: white;
            font-size: 11px;
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        layout.addWidget(self.led)
        layout.addWidget(self.label)
        layout.addStretch()

        self.setLayout(layout)

    def SetState(self, state):
        """Update signal state"""
        self.led.SetState(state)


# ============================================================
# Bit Checkbox
# ============================================================

class BitCheckBox(QCheckBox):
    """Styled checkbox for instruction bits"""

    def __init__(self, bitText):
        super().__init__(bitText)

        self.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 13px;
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                background: #2f2f2f;
                border: 1px solid #444;
            }

            QCheckBox::indicator:checked {
                background: #35ff5a;
                border: 1px solid #35ff5a;
            }
        """)
