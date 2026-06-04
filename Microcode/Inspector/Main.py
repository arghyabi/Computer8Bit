import sys
from PySide6.QtWidgets import QApplication

import uCodeInspector

# ============================================================
# Main
# ============================================================
def Main():
    app = QApplication(sys.argv)
    window = uCodeInspector.VerifyWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    Main()
