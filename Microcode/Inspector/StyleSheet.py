class StyleSheet:
    mainWindowStyle = """
        QWidget {
            background-color: #181818;
            color: white;
        }

        QGroupBox {
            border: 1px solid #333;
            margin-top: 8px;
            font-size: 13px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        QTextEdit {
            background-color: #050505;
            border: 1px solid #333;
            font-family: Menlo;
            font-size: 12px;
        }

        QListWidget {
            background-color: #050505;
            border: 1px solid #333;
            font-family: Menlo;
            font-size: 12px;
        }

        QPushButton {
            background-color: #2d2d2d;
            border: 1px solid #444;
            padding: 6px;
        }

        QPushButton:hover {
            background-color: #404040;
        }

        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #444;
            padding: 4px;
        }

        QSpinBox {
            background-color: #2d2d2d;
            border: 1px solid #444;
            padding: 4px;
        }
    """
